"""
Semantic Drift Detector Service
================================

Session 914.3: Semantic Quality Gates for Initiative Pipeline

Problem: Stage documents can drift away from the original initiative intent,
producing "beautiful docs for the wrong thing." The auto-progression system
only checks structural quality, not semantic alignment.

Solution: Use embeddings to measure semantic similarity between:
1. Original initiative description/dream content
2. Current stage document content

If drift exceeds threshold, block progression and flag for human review.

Usage:
    from core.services.semantic_drift_detector import (
        check_semantic_drift,
        get_drift_detector
    )

    # Check a single stage
    result = check_semantic_drift(initiative_stage)
    if result['has_drift']:
        print(f"Drift detected: {result['drift_score']:.0%}")
        print(f"Reason: {result['drift_reason']}")
"""

import logging
import hashlib
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from decimal import Decimal

import numpy as np
from django.core.cache import cache

logger = logging.getLogger(__name__)

# Drift thresholds (1 - similarity score)
# Lower threshold = stricter alignment required
DRIFT_THRESHOLDS = {
    'strict': 0.25,      # 75%+ similarity required
    'balanced': 0.35,    # 65%+ similarity required
    'relaxed': 0.45,     # 55%+ similarity required
}

DEFAULT_THRESHOLD = 'balanced'

# Stage-specific thresholds (some stages naturally diverge more)
STAGE_DRIFT_ADJUSTMENTS = {
    1: 0.0,    # Research Brief should closely match intent
    2: 0.05,   # Prototype Plan can diverge slightly
    3: 0.05,   # Evaluation Protocol should match intent
    4: 0.10,   # Technical Design may have implementation details
    5: 0.10,   # Pilot Execution may have practical adjustments
}


@dataclass
class DriftResult:
    """Result from semantic drift check."""
    has_drift: bool
    drift_score: float  # 0 = perfect alignment, 1 = complete drift
    similarity_score: float  # 0 = unrelated, 1 = identical
    threshold_used: float
    drift_reason: str
    source_text_preview: str
    stage_text_preview: str


class SemanticDriftDetector:
    """
    Detects semantic drift between initiative intent and stage documents.

    Uses OpenAI embeddings to compare content and calculate alignment scores.
    """

    CACHE_KEY_PREFIX = "semantic_drift:"
    CACHE_TTL = 3600 * 6  # 6 hours for drift embeddings

    def __init__(self):
        self._embedding_service = None

    @property
    def embedding_service(self):
        """Lazy-load centralized EmbeddingService."""
        if self._embedding_service is None:
            from core.services.embedding_service import get_embedding_service
            self._embedding_service = get_embedding_service()
        return self._embedding_service

    def _generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for text using centralized EmbeddingService."""
        try:
            result = self.embedding_service.create_embedding(
                text=text[:6000],  # Truncate to avoid token limits
                agent_name='SemanticDriftDetector'
            )
            return result.embedding
        except Exception as e:
            logger.error(f"[Session 914.3] Embedding generation failed: {e}")
            return None

    def _get_cached_embedding(self, text: str, key_suffix: str = "") -> Optional[List[float]]:
        """Get embedding from cache or generate new one."""
        text_hash = hashlib.md5(text.encode()).hexdigest()[:16]
        cache_key = f"{self.CACHE_KEY_PREFIX}{key_suffix}:{text_hash}"

        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        embedding = self._generate_embedding(text)
        if embedding:
            cache.set(cache_key, embedding, self.CACHE_TTL)

        return embedding

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        a_arr = np.array(a)
        b_arr = np.array(b)
        norm_a = np.linalg.norm(a_arr)
        norm_b = np.linalg.norm(b_arr)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(a_arr, b_arr) / (norm_a * norm_b))

    def _build_source_text(self, initiative) -> str:
        """Build source text from initiative intent."""
        parts = []

        # Initiative name and description
        if initiative.name:
            parts.append(f"Initiative: {initiative.name}")
        if initiative.description:
            parts.append(f"Description: {initiative.description[:1000]}")

        # Original dream content if available
        try:
            if hasattr(initiative, 'source_dreams') and initiative.source_dreams.exists():
                dream = initiative.source_dreams.first()
                if dream:
                    if dream.title:
                        parts.append(f"Original Dream: {dream.title}")
                    if dream.content:
                        parts.append(f"Dream Content: {dream.content[:1000]}")
        except Exception as e:
            logger.debug(f"[Session 914.3] Could not get source dream: {e}")

        # Stop rule if set (defines success criteria)
        if initiative.stop_rule:
            parts.append(f"Success Criteria: {initiative.stop_rule}")

        return "\n".join(parts)

    def _build_stage_text(self, initiative_stage) -> str:
        """Build text from stage document content."""
        parts = []

        if initiative_stage.document:
            doc = initiative_stage.document
            if doc.title:
                parts.append(f"Title: {doc.title}")
            if doc.full_text:
                parts.append(f"Content: {doc.full_text[:2000]}")
            elif doc.content:
                parts.append(f"Content: {doc.content[:2000]}")

        return "\n".join(parts) if parts else ""

    def check_drift(
        self,
        initiative_stage,
        threshold_mode: str = DEFAULT_THRESHOLD
    ) -> DriftResult:
        """
        Check semantic drift between initiative intent and stage document.

        Args:
            initiative_stage: InitiativeStage instance
            threshold_mode: 'strict', 'balanced', or 'relaxed'

        Returns:
            DriftResult with drift analysis
        """
        initiative = initiative_stage.initiative
        stage_num = initiative_stage.stage

        # Build texts
        source_text = self._build_source_text(initiative)
        stage_text = self._build_stage_text(initiative_stage)

        if not source_text:
            return DriftResult(
                has_drift=False,
                drift_score=0.0,
                similarity_score=1.0,
                threshold_used=0.0,
                drift_reason="No source text available for comparison",
                source_text_preview="",
                stage_text_preview=stage_text[:200] if stage_text else ""
            )

        if not stage_text:
            return DriftResult(
                has_drift=True,
                drift_score=1.0,
                similarity_score=0.0,
                threshold_used=0.0,
                drift_reason="Stage document is empty",
                source_text_preview=source_text[:200],
                stage_text_preview=""
            )

        # Generate embeddings
        source_embedding = self._get_cached_embedding(source_text, f"init_{initiative.id}")
        stage_embedding = self._get_cached_embedding(stage_text, f"stage_{initiative_stage.id}")

        if not source_embedding or not stage_embedding:
            logger.warning(f"[Session 914.3] Could not generate embeddings for drift check")
            return DriftResult(
                has_drift=False,
                drift_score=0.0,
                similarity_score=0.5,
                threshold_used=0.0,
                drift_reason="Embedding generation failed - skipping drift check",
                source_text_preview=source_text[:200],
                stage_text_preview=stage_text[:200]
            )

        # Calculate similarity
        similarity = self._cosine_similarity(source_embedding, stage_embedding)
        drift_score = 1.0 - similarity

        # Get threshold with stage adjustment
        base_threshold = DRIFT_THRESHOLDS.get(threshold_mode, DRIFT_THRESHOLDS['balanced'])
        stage_adjustment = STAGE_DRIFT_ADJUSTMENTS.get(stage_num, 0.0)
        threshold = base_threshold + stage_adjustment

        has_drift = drift_score > threshold

        # Build reason
        if has_drift:
            drift_reason = (
                f"Stage {stage_num} document has drifted from initiative intent "
                f"(similarity: {similarity:.0%}, threshold: {1-threshold:.0%})"
            )
        else:
            drift_reason = (
                f"Stage {stage_num} document aligns with initiative intent "
                f"(similarity: {similarity:.0%})"
            )

        logger.info(
            f"[Session 914.3] Drift check for {initiative.name[:50]}: "
            f"similarity={similarity:.2f}, drift={drift_score:.2f}, "
            f"threshold={threshold:.2f}, has_drift={has_drift}"
        )

        return DriftResult(
            has_drift=has_drift,
            drift_score=drift_score,
            similarity_score=similarity,
            threshold_used=threshold,
            drift_reason=drift_reason,
            source_text_preview=source_text[:200],
            stage_text_preview=stage_text[:200]
        )

    def check_initiative_drift(self, initiative_id: str) -> Dict[str, Any]:
        """
        Check drift for all stages of an initiative.

        Returns summary of drift across all stages.
        """
        from core.models_document_registry import Initiative, InitiativeStage

        try:
            initiative = Initiative.objects.get(id=initiative_id)
        except Initiative.DoesNotExist:
            return {'success': False, 'error': 'Initiative not found'}

        stages = InitiativeStage.objects.filter(
            initiative=initiative,
            document__isnull=False
        ).order_by('stage')

        results = []
        total_drift = 0.0
        drift_count = 0

        for stage in stages:
            drift_result = self.check_drift(stage)
            results.append({
                'stage': stage.stage,
                'has_drift': drift_result.has_drift,
                'drift_score': drift_result.drift_score,
                'similarity_score': drift_result.similarity_score,
                'reason': drift_result.drift_reason
            })
            total_drift += drift_result.drift_score
            if drift_result.has_drift:
                drift_count += 1

        avg_drift = total_drift / len(results) if results else 0.0

        return {
            'success': True,
            'initiative_id': str(initiative_id),
            'initiative_name': initiative.name,
            'stages_checked': len(results),
            'stages_with_drift': drift_count,
            'average_drift': avg_drift,
            'overall_alignment': 1.0 - avg_drift,
            'stage_results': results
        }


# Singleton instance
_detector_instance = None


def get_drift_detector() -> SemanticDriftDetector:
    """Get singleton instance of SemanticDriftDetector."""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = SemanticDriftDetector()
    return _detector_instance


def check_semantic_drift(initiative_stage, threshold_mode: str = DEFAULT_THRESHOLD) -> Dict[str, Any]:
    """
    Convenience function to check semantic drift for a stage.

    Args:
        initiative_stage: InitiativeStage instance
        threshold_mode: 'strict', 'balanced', or 'relaxed'

    Returns:
        Dict with drift analysis
    """
    detector = get_drift_detector()
    result = detector.check_drift(initiative_stage, threshold_mode)

    return {
        'has_drift': result.has_drift,
        'drift_score': result.drift_score,
        'similarity_score': result.similarity_score,
        'threshold_used': result.threshold_used,
        'drift_reason': result.drift_reason,
        'source_preview': result.source_text_preview,
        'stage_preview': result.stage_text_preview
    }

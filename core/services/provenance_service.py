"""
Provenance Service - Session 295
================================

Comprehensive service for content provenance, ethics audit, and originality scoring.
Addresses customer pain points:
- Gap #3: Provenance & Attribution
- Gap #4: Bias & Ethics Transparency
- Gap #2: AI Slop Differentiation
"""

import hashlib
import hmac
import logging
import os
import json
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from dataclasses import dataclass

from django.utils import timezone
from django.conf import settings

logger = logging.getLogger(__name__)


@dataclass
class ProvenanceResult:
    """Result of provenance creation."""
    success: bool
    provenance_id: Optional[str] = None
    content_hash: Optional[str] = None
    perceptual_hash: Optional[str] = None
    certificate: Optional[Dict] = None
    error: Optional[str] = None


@dataclass
class AuditResult:
    """Result of content audit."""
    success: bool
    safety_score: int = 100
    bias_detected: bool = False
    bias_categories: List[str] = None
    ethics_flags: List[str] = None
    prompt_suggestions: List[str] = None
    recommendations: List[str] = None
    transparency_card: Optional[Dict] = None
    error: Optional[str] = None


@dataclass
class OriginalityResult:
    """Result of originality scoring."""
    success: bool
    overall_score: int = 50
    prompt_originality: int = 50
    style_originality: int = 50
    composition_originality: int = 50
    trend_similarity: int = 50
    generic_patterns: List[str] = None
    suggestions: List[str] = None
    verdict: str = ""
    error: Optional[str] = None


class ProvenanceService:
    """
    Service for managing content provenance and attribution.

    Features:
    - SHA-256 content fingerprinting
    - Perceptual hashing for image similarity
    - HMAC signatures for timestamp verification
    - Certificate generation for ownership proof
    - Derivative tracking
    """

    def __init__(self):
        self.secret_key = os.getenv('PROVENANCE_SECRET_KEY', 'ai-studio-provenance-key')

    def create_provenance(
        self,
        image_history,
        user,
        image_bytes: bytes,
        generation_params: dict = None
    ) -> ProvenanceResult:
        """
        Create provenance record for generated content.

        Args:
            image_history: ImageHistory instance
            user: User who created the content
            image_bytes: Raw bytes of the content
            generation_params: Generation parameters (prompt, model, style, etc.)

        Returns:
            ProvenanceResult with provenance details
        """
        try:
            from core.models_unified_system import ContentProvenance

            # Create provenance record (model handles hashing)
            provenance = ContentProvenance.create_for_image(
                image_history=image_history,
                user=user,
                image_bytes=image_bytes,
                generation_params=generation_params
            )

            logger.info(f"Created provenance record: {provenance.id}")

            return ProvenanceResult(
                success=True,
                provenance_id=str(provenance.id),
                content_hash=provenance.content_hash,
                perceptual_hash=provenance.perceptual_hash,
            )

        except Exception as e:
            logger.error(f"Failed to create provenance: {e}")
            return ProvenanceResult(success=False, error=str(e))

    def generate_certificate(self, provenance_id: str) -> ProvenanceResult:
        """
        Generate an exportable certificate of provenance.

        Args:
            provenance_id: UUID of the provenance record

        Returns:
            ProvenanceResult with certificate dict
        """
        try:
            from core.models_unified_system import ContentProvenance

            provenance = ContentProvenance.objects.get(id=provenance_id)
            certificate = provenance.generate_certificate()

            logger.info(f"Generated certificate for: {provenance_id}")

            return ProvenanceResult(
                success=True,
                provenance_id=provenance_id,
                certificate=certificate
            )

        except Exception as e:
            logger.error(f"Failed to generate certificate: {e}")
            return ProvenanceResult(success=False, error=str(e))

    def verify_content(self, content_bytes: bytes) -> Optional[Dict]:
        """
        Verify if content exists in our provenance records.

        Args:
            content_bytes: Raw bytes to verify

        Returns:
            Dict with provenance info if found, None otherwise
        """
        try:
            from core.models_unified_system import ContentProvenance

            content_hash = hashlib.sha256(content_bytes).hexdigest()

            matches = ContentProvenance.find_by_hash(content_hash)
            if matches.exists():
                provenance = matches.first()
                return {
                    'verified': True,
                    'provenance_id': str(provenance.id),
                    'creator': provenance.creator.username,
                    'created_at': provenance.created_at.isoformat(),
                    'derivative_type': provenance.derivative_type,
                }

            return None

        except Exception as e:
            logger.error(f"Verification failed: {e}")
            return None

    def find_similar_images(
        self,
        perceptual_hash: str,
        threshold: int = 10
    ) -> List[Tuple]:
        """
        Find similar images by perceptual hash.

        Args:
            perceptual_hash: pHash string to compare
            threshold: Hamming distance threshold (lower = more similar)

        Returns:
            List of (provenance, distance) tuples
        """
        try:
            from core.models_unified_system import ContentProvenance
            return ContentProvenance.find_similar(perceptual_hash, threshold)
        except Exception as e:
            logger.error(f"Similar image search failed: {e}")
            return []

    def get_derivative_chain(self, provenance_id: str) -> List[Dict]:
        """
        Get the full derivative chain for a piece of content.

        Args:
            provenance_id: Starting provenance ID

        Returns:
            List of provenance records in the chain
        """
        try:
            from core.models_unified_system import ContentProvenance

            chain = []
            current = ContentProvenance.objects.get(id=provenance_id)

            # Walk up the chain to original
            while current:
                chain.append({
                    'id': str(current.id),
                    'type': current.derivative_type,
                    'created_at': current.created_at.isoformat(),
                    'creator': current.creator.username,
                })
                current = current.parent_provenance

            chain.reverse()  # Original first
            return chain

        except Exception as e:
            logger.error(f"Failed to get derivative chain: {e}")
            return []


class ContentAuditService:
    """
    Service for bias detection and ethics transparency.

    Features:
    - Prompt safety analysis
    - Known model bias documentation
    - Representation analysis
    - User-friendly transparency cards
    """

    # Known biases by model (documentation purposes)
    MODEL_KNOWN_BIASES = {
        'core': [
            'Tends toward Western beauty standards',
            'May underrepresent certain ethnicities',
        ],
        'sdxl': [
            'Default skin tones may lack diversity',
            'Cultural imagery may be stereotyped',
        ],
        'sd3': [
            'Improved diversity but still Western-centric',
            'Lighting may favor lighter skin tones',
        ],
        'ultra': [
            'Most diverse model, still monitor outputs',
        ],
    }

    # Prompt keywords that may indicate bias concerns
    BIAS_KEYWORDS = {
        'gender': ['beautiful woman', 'handsome man', 'sexy', 'attractive'],
        'racial': ['exotic', 'ethnic', 'traditional', 'tribal'],
        'cultural': ['primitive', 'oriental', 'western'],
        'ageism': ['young', 'old', 'elderly', 'youthful'],
    }

    # Safety concern keywords
    SAFETY_KEYWORDS = [
        'violent', 'gore', 'blood', 'weapon', 'nsfw', 'nude',
        'child', 'minor', 'underage', 'illegal',
    ]

    def audit_prompt(self, prompt: str) -> AuditResult:
        """
        Analyze a prompt for potential bias and safety concerns.

        Args:
            prompt: The generation prompt to analyze

        Returns:
            AuditResult with analysis
        """
        prompt_lower = prompt.lower()

        # Check for safety concerns
        safety_score = 100
        safety_issues = []
        for keyword in self.SAFETY_KEYWORDS:
            if keyword in prompt_lower:
                safety_score -= 20
                safety_issues.append(f"Contains '{keyword}'")
        safety_score = max(0, safety_score)

        # Check for bias indicators
        bias_detected = False
        bias_categories = []
        for category, keywords in self.BIAS_KEYWORDS.items():
            for keyword in keywords:
                if keyword in prompt_lower:
                    bias_detected = True
                    if category not in bias_categories:
                        bias_categories.append(category)

        # Generate suggestions
        suggestions = []
        if 'beautiful' in prompt_lower or 'handsome' in prompt_lower:
            suggestions.append("Consider using 'confident' or 'professional' instead of beauty descriptors")
        if 'exotic' in prompt_lower:
            suggestions.append("Replace 'exotic' with specific cultural or regional descriptors")
        if 'traditional' in prompt_lower:
            suggestions.append("Specify which tradition to avoid stereotyping")

        # Recommendations
        recommendations = []
        if bias_detected:
            recommendations.append("Review output for unintended stereotypes")
            recommendations.append("Consider generating multiple variations")
        if safety_score < 80:
            recommendations.append("Review content guidelines before publishing")

        return AuditResult(
            success=True,
            safety_score=safety_score,
            bias_detected=bias_detected,
            bias_categories=bias_categories,
            ethics_flags=safety_issues,
            prompt_suggestions=suggestions,
            recommendations=recommendations,
        )

    def audit_content(
        self,
        provenance_id: str,
        model_used: str = None
    ) -> AuditResult:
        """
        Create a full audit record for generated content.

        Args:
            provenance_id: Provenance record to audit
            model_used: Model used for generation (for bias documentation)

        Returns:
            AuditResult with full analysis
        """
        try:
            from core.models_unified_system import ContentProvenance, ContentAuditResult

            provenance = ContentProvenance.objects.get(id=provenance_id)
            prompt = provenance.generation_params.get('prompt', '')

            # Analyze prompt
            prompt_result = self.audit_prompt(prompt)

            # Get model biases
            model_biases = self.MODEL_KNOWN_BIASES.get(model_used, [])

            # Create audit record
            audit = ContentAuditResult.objects.create(
                provenance=provenance,
                overall_safety_score=prompt_result.safety_score,
                bias_detected=prompt_result.bias_detected,
                bias_categories=prompt_result.bias_categories or [],
                bias_details=f"Detected in prompt: {', '.join(prompt_result.bias_categories or [])}",
                ethics_flags=prompt_result.ethics_flags or [],
                prompt_safety_score=prompt_result.safety_score,
                prompt_suggestions=prompt_result.prompt_suggestions or [],
                model_known_biases=model_biases,
                recommendations=prompt_result.recommendations or [],
            )

            logger.info(f"Created audit record for provenance: {provenance_id}")

            return AuditResult(
                success=True,
                safety_score=audit.overall_safety_score,
                bias_detected=audit.bias_detected,
                bias_categories=audit.bias_categories,
                ethics_flags=audit.ethics_flags,
                prompt_suggestions=audit.prompt_suggestions,
                recommendations=audit.recommendations,
                transparency_card=audit.generate_transparency_card(),
            )

        except Exception as e:
            logger.error(f"Content audit failed: {e}")
            return AuditResult(success=False, error=str(e))


class OriginalityService:
    """
    Service for originality scoring and differentiation.

    Features:
    - Prompt uniqueness analysis
    - Style trend comparison
    - Generic AI pattern detection
    - Differentiation suggestions
    """

    # Common generic AI patterns to flag
    GENERIC_PATTERNS = [
        'perfect lighting',
        'studio lighting',
        'smooth skin',
        'perfect face',
        'photorealistic',
        'hyper realistic',
        '8k',
        'unreal engine',
        'octane render',
        'artstation',
        'trending on artstation',
        'highly detailed',
        'masterpiece',
    ]

    # Overused style combinations
    OVERUSED_COMBOS = [
        ('cyberpunk', 'neon'),
        ('fantasy', 'dragon'),
        ('anime', 'girl'),
        ('portrait', 'beautiful'),
    ]

    # More original alternatives
    ORIGINALITY_SUGGESTIONS = {
        'perfect lighting': 'Try: dramatic shadows, harsh noon sun, candlelight',
        'photorealistic': 'Try: illustrated, stylized, textured brush strokes',
        'trending on artstation': 'Remove this - it adds nothing unique',
        'highly detailed': 'Try: intentionally rough, sketchy, impressionistic',
        'masterpiece': 'Let the work speak for itself without labels',
    }

    def analyze_prompt_originality(self, prompt: str) -> OriginalityResult:
        """
        Analyze a prompt for originality.

        Args:
            prompt: The generation prompt

        Returns:
            OriginalityResult with analysis
        """
        prompt_lower = prompt.lower()

        # Count generic patterns
        generic_found = []
        for pattern in self.GENERIC_PATTERNS:
            if pattern in prompt_lower:
                generic_found.append(pattern)

        # Calculate prompt originality
        generic_penalty = len(generic_found) * 10
        prompt_originality = max(0, 100 - generic_penalty)

        # Check for overused combos
        combo_penalty = 0
        for combo in self.OVERUSED_COMBOS:
            if all(word in prompt_lower for word in combo):
                combo_penalty += 15

        style_originality = max(0, 100 - combo_penalty)

        # Overall score
        overall = int((prompt_originality + style_originality) / 2)

        # Generate suggestions
        suggestions = []
        for pattern in generic_found:
            if pattern in self.ORIGINALITY_SUGGESTIONS:
                suggestions.append(self.ORIGINALITY_SUGGESTIONS[pattern])

        if not suggestions and overall < 60:
            suggestions.append("Add unusual adjectives or unexpected combinations")
            suggestions.append("Specify a unique time period, location, or mood")
            suggestions.append("Mix styles that aren't typically combined")

        # Verdict
        if overall >= 80:
            verdict = "Highly Original - Your prompt stands out!"
        elif overall >= 60:
            verdict = "Moderately Original - Some unique elements"
        elif overall >= 40:
            verdict = "Average - Consider the suggestions below"
        else:
            verdict = "Generic - High risk of 'AI slop' appearance"

        return OriginalityResult(
            success=True,
            overall_score=overall,
            prompt_originality=prompt_originality,
            style_originality=style_originality,
            composition_originality=70,  # Would need image analysis
            trend_similarity=100 - overall,
            generic_patterns=generic_found,
            suggestions=suggestions,
            verdict=verdict,
        )

    def score_content(self, provenance_id: str) -> OriginalityResult:
        """
        Create originality score record for content.

        Args:
            provenance_id: Provenance record to score

        Returns:
            OriginalityResult with full analysis
        """
        try:
            from core.models_unified_system import ContentProvenance, OriginalityScore

            provenance = ContentProvenance.objects.get(id=provenance_id)
            prompt = provenance.generation_params.get('prompt', '')

            # Analyze
            analysis = self.analyze_prompt_originality(prompt)

            # Create record
            score = OriginalityScore.objects.create(
                provenance=provenance,
                overall_originality=analysis.overall_score,
                prompt_originality=analysis.prompt_originality,
                style_originality=analysis.style_originality,
                composition_originality=analysis.composition_originality,
                trend_similarity=analysis.trend_similarity,
                generic_patterns_detected=analysis.generic_patterns or [],
                differentiation_suggestions=analysis.suggestions or [],
                uniqueness_percentile=analysis.overall_score,  # Simplified
            )

            logger.info(f"Created originality score for provenance: {provenance_id}")

            return OriginalityResult(
                success=True,
                overall_score=score.overall_originality,
                prompt_originality=score.prompt_originality,
                style_originality=score.style_originality,
                composition_originality=score.composition_originality,
                trend_similarity=score.trend_similarity,
                generic_patterns=score.generic_patterns_detected,
                suggestions=score.differentiation_suggestions,
                verdict=score._get_verdict(),
            )

        except Exception as e:
            logger.error(f"Originality scoring failed: {e}")
            return OriginalityResult(success=False, error=str(e))

    def get_alternative_prompts(self, original_prompt: str, count: int = 3) -> List[str]:
        """
        Generate more original prompt alternatives.

        Args:
            original_prompt: The original prompt
            count: Number of alternatives to generate

        Returns:
            List of alternative prompts
        """
        # This would ideally use GPT to generate alternatives
        # For now, return simple modifications
        alternatives = []

        prompt_lower = original_prompt.lower()

        # Remove generic patterns
        cleaned = original_prompt
        for pattern in self.GENERIC_PATTERNS:
            cleaned = cleaned.replace(pattern, '')
        cleaned = ' '.join(cleaned.split())  # Clean up whitespace

        if cleaned != original_prompt:
            alternatives.append(f"Simplified: {cleaned}")

        # Add style variations
        if 'portrait' in prompt_lower:
            alternatives.append(f"{original_prompt}, in the style of Renaissance chiaroscuro")
            alternatives.append(f"{original_prompt}, with Wes Anderson color palette")

        if 'landscape' in prompt_lower:
            alternatives.append(f"{original_prompt}, painted with palette knife textures")
            alternatives.append(f"{original_prompt}, as seen through morning mist")

        # Fallback suggestions
        if len(alternatives) < count:
            alternatives.append(f"{original_prompt}, with intentional imperfections")
            alternatives.append(f"{original_prompt}, captured in a candid moment")

        return alternatives[:count]


# Convenience function for one-shot provenance + audit + originality
def analyze_generated_content(
    image_history,
    user,
    image_bytes: bytes,
    generation_params: dict = None,
    model_used: str = None
) -> Dict[str, Any]:
    """
    Complete analysis pipeline for generated content.

    Creates provenance, runs audit, and scores originality.

    Returns:
        Dict with all analysis results
    """
    provenance_service = ProvenanceService()
    audit_service = ContentAuditService()
    originality_service = OriginalityService()

    # Create provenance
    prov_result = provenance_service.create_provenance(
        image_history=image_history,
        user=user,
        image_bytes=image_bytes,
        generation_params=generation_params
    )

    if not prov_result.success:
        return {'success': False, 'error': prov_result.error}

    # Run audit
    audit_result = audit_service.audit_content(
        provenance_id=prov_result.provenance_id,
        model_used=model_used
    )

    # Score originality
    orig_result = originality_service.score_content(
        provenance_id=prov_result.provenance_id
    )

    return {
        'success': True,
        'provenance': {
            'id': prov_result.provenance_id,
            'content_hash': prov_result.content_hash,
            'perceptual_hash': prov_result.perceptual_hash,
        },
        'audit': {
            'safety_score': audit_result.safety_score,
            'bias_detected': audit_result.bias_detected,
            'bias_categories': audit_result.bias_categories,
            'transparency_card': audit_result.transparency_card,
        },
        'originality': {
            'overall_score': orig_result.overall_score,
            'verdict': orig_result.verdict,
            'suggestions': orig_result.suggestions,
            'generic_patterns': orig_result.generic_patterns,
        }
    }

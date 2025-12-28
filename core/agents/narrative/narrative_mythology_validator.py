"""
Session 509: Narrative Mythology Validator

Prevents hallucinations in narrative evidence by:
1. Verifying source URLs are real and accessible
2. Requiring multiple corroborating sources for high-confidence shifts
3. Flagging single-source shifts as "unverified"
4. Validating evidence content for unrealistic claims

Integration with Narrative Drift Coordinator to ensure data quality.
"""

import re
import logging
from typing import Dict, Any, Tuple
from datetime import datetime, timedelta
from urllib.parse import urlparse
from decimal import Decimal

logger = logging.getLogger(__name__)


# =============================================================================
# Known Reliable Sources by Domain
# =============================================================================
# Used to boost confidence for evidence from authoritative sources

AUTHORITATIVE_SOURCES = {
    'climate': [
        'noaa.gov', 'epa.gov', 'nasa.gov', 'ipcc.ch', 'nature.com',
        'sciencedaily.com', 'carbonbrief.org', 'climatecentral.org'
    ],
    'health': [
        'nih.gov', 'cdc.gov', 'who.int', 'nejm.org', 'thelancet.com',
        'jamanetwork.com', 'bmj.com', 'nature.com/medicine'
    ],
    'markets': [
        'sec.gov', 'federalreserve.gov', 'treasury.gov', 'imf.org',
        'bloomberg.com', 'reuters.com', 'wsj.com', 'ft.com'
    ],
    'politics': [
        'congress.gov', 'whitehouse.gov', 'state.gov', 'supremecourt.gov',
        'apnews.com', 'reuters.com', 'c-span.org'
    ],
    'geopolitics': [
        'un.org', 'nato.int', 'state.gov', 'foreignaffairs.com',
        'cfr.org', 'brookings.edu', 'rand.org'
    ],
    'tech': [
        'ieee.org', 'acm.org', 'arxiv.org', 'techcrunch.com',
        'wired.com', 'arstechnica.com', 'technologyreview.com'
    ],
    'crypto': [
        'sec.gov', 'cftc.gov', 'coindesk.com', 'theblock.co',
        'messari.io', 'chainalysis.com'
    ],
    'culture': [
        'nytimes.com', 'newyorker.com', 'theatlantic.com',
        'washingtonpost.com', 'bbc.com', 'npr.org'
    ]
}

# Known unreliable sources (satire, clickbait, etc.)
UNRELIABLE_SOURCES = [
    'theonion.com', 'babylonbee.com', 'clickhole.com',
    'worldnewsdailyreport.com', 'beforeitsnews.com',
    'dailybuzzlive.com', 'empirenews.net', 'huzlers.com'
]


class NarrativeMythologyValidator:
    """
    Validates narrative evidence to prevent hallucinations and ensure quality.

    Features:
    1. URL validation - checks if source URLs are real and accessible
    2. Source credibility scoring - prefers authoritative sources
    3. Corroboration checking - requires multiple sources for high confidence
    4. Content validation - detects unrealistic claims
    """

    # Minimum sources required for different confidence levels
    MIN_SOURCES_FOR_HIGH_CONFIDENCE = 3  # 70%+ confidence
    MIN_SOURCES_FOR_SHIFT_DETECTION = 2  # To detect a real shift

    # Unrealistic claim patterns (narrative-specific)
    NARRATIVE_MYTHS = [
        r'(?:everyone|all\s+people|the\s+entire\s+world)\s+(?:believes?|agrees?|knows?)',  # Universal claims
        r'(?:definitely|certainly|absolutely|100%)\s+(?:will|going\s+to)',  # Certainty claims
        r'(?:proven|confirmed)\s+(?:beyond\s+doubt|definitively|conclusively)',  # Proof claims
        r'(?:no\s+one|nobody)\s+(?:believes?|supports?|thinks?)',  # Absolute negatives
        r'(?:always|never)\s+(?:happens?|works?|fails?)',  # Absolute time claims
        r'(?:complete|total)\s+(?:collapse|failure|success)',  # Extreme outcomes
        r'(?:secret|hidden)\s+(?:agenda|plan|truth)',  # Conspiracy language
        r'(?:mainstream\s+media|msm)\s+(?:lies?|hiding|covers?\s+up)',  # MSM conspiracy
        r'(?:wake\s+up|sheeple|they\s+don\'t\s+want\s+you\s+to\s+know)',  # Conspiracy rhetoric
    ]

    # Cache for URL validation (avoid repeated checks)
    _url_cache: Dict[str, Tuple[bool, datetime]] = {}
    URL_CACHE_TTL = timedelta(hours=1)

    def __init__(self):
        """Initialize the validator."""
        self.validation_stats = {
            'total_checks': 0,
            'valid_sources': 0,
            'invalid_sources': 0,
            'myth_detections': 0,
            'corroboration_failures': 0
        }
        logger.info("🛡️ NarrativeMythologyValidator initialized")

    def validate_evidence(
        self,
        source_url: str,
        content: str,
        domain: str,
        existing_evidence_count: int = 0
    ) -> Dict[str, Any]:
        """
        Validate a piece of narrative evidence.

        Args:
            source_url: URL of the evidence source
            content: Text content of the evidence
            domain: Narrative domain (climate, health, etc.)
            existing_evidence_count: How many other sources already support this claim

        Returns:
            Dict with validation results:
            - valid: bool - whether evidence should be stored
            - confidence_multiplier: float - multiplier for confidence score
            - is_authoritative: bool - from known authoritative source
            - warnings: list - any warnings about the evidence
            - verified: bool - fully verified evidence
        """
        self.validation_stats['total_checks'] += 1

        result = {
            'valid': True,
            'confidence_multiplier': 1.0,
            'is_authoritative': False,
            'is_unreliable': False,
            'warnings': [],
            'verified': False,
            'source_quality': 'unknown'
        }

        # 1. Validate URL format
        url_valid, url_warning = self._validate_url_format(source_url)
        if not url_valid:
            result['valid'] = False
            result['warnings'].append(url_warning)
            self.validation_stats['invalid_sources'] += 1
            return result

        # 2. Check if source is known unreliable
        if self._is_unreliable_source(source_url):
            result['valid'] = False
            result['is_unreliable'] = True
            result['warnings'].append(f"Source is known unreliable: {source_url[:50]}")
            self.validation_stats['invalid_sources'] += 1
            return result

        # 3. Check if source is authoritative
        if self._is_authoritative_source(source_url, domain):
            result['is_authoritative'] = True
            result['confidence_multiplier'] = 1.3  # 30% boost for authoritative
            result['source_quality'] = 'authoritative'
            self.validation_stats['valid_sources'] += 1
        else:
            result['source_quality'] = 'general'

        # 4. Validate content for mythology (unrealistic claims)
        myth_result = self._check_for_myths(content)
        if myth_result['has_myths']:
            result['confidence_multiplier'] *= 0.5  # 50% penalty
            result['warnings'].extend(myth_result['warnings'])
            self.validation_stats['myth_detections'] += 1

        # 5. Check corroboration for high confidence
        if existing_evidence_count >= self.MIN_SOURCES_FOR_HIGH_CONFIDENCE:
            result['verified'] = True
            result['confidence_multiplier'] *= 1.2  # Boost for corroboration
        elif existing_evidence_count < self.MIN_SOURCES_FOR_SHIFT_DETECTION:
            result['warnings'].append(
                f"Low corroboration: only {existing_evidence_count + 1} source(s)"
            )

        return result

    def validate_shift(
        self,
        shift_data: Dict[str, Any],
        evidence_count: int,
        unique_source_count: int
    ) -> Dict[str, Any]:
        """
        Validate a narrative shift detection.

        Args:
            shift_data: The shift information
            evidence_count: Total evidence supporting shift
            unique_source_count: Number of unique sources

        Returns:
            Dict with validation results:
            - valid: bool - whether shift should be recorded
            - verified: bool - shift is well-corroborated
            - confidence_adjustment: float - adjustment to confidence score
            - warnings: list - any warnings
        """
        result = {
            'valid': True,
            'verified': False,
            'confidence_adjustment': 0.0,
            'warnings': []
        }

        # Require minimum sources for shift detection
        if unique_source_count < self.MIN_SOURCES_FOR_SHIFT_DETECTION:
            result['verified'] = False
            result['confidence_adjustment'] = -0.2  # Reduce confidence
            result['warnings'].append(
                f"⚠️ UNVERIFIED: Only {unique_source_count} unique source(s). "
                f"Requires {self.MIN_SOURCES_FOR_SHIFT_DETECTION}+ for verification."
            )
            self.validation_stats['corroboration_failures'] += 1

        # High confidence requires more sources
        if unique_source_count >= self.MIN_SOURCES_FOR_HIGH_CONFIDENCE:
            result['verified'] = True
            result['confidence_adjustment'] = 0.1  # Boost confidence

        # Check evidence density (evidence per source)
        if unique_source_count > 0:
            density = evidence_count / unique_source_count
            if density > 5:
                result['warnings'].append(
                    f"High evidence density ({density:.1f}x) - may indicate duplicate sources"
                )

        return result

    def _validate_url_format(self, url: str) -> Tuple[bool, str]:
        """Validate URL format without making HTTP request."""
        if not url:
            return False, "Empty URL"

        try:
            parsed = urlparse(url)

            # Must have scheme and netloc
            if not parsed.scheme or not parsed.netloc:
                return False, f"Invalid URL format: {url[:50]}"

            # Must be http or https
            if parsed.scheme not in ('http', 'https'):
                return False, f"Invalid URL scheme: {parsed.scheme}"

            # Basic domain validation
            if '.' not in parsed.netloc:
                return False, f"Invalid domain: {parsed.netloc}"

            return True, ""

        except Exception as e:
            return False, f"URL parse error: {str(e)[:50]}"

    def _is_unreliable_source(self, url: str) -> bool:
        """Check if URL is from a known unreliable source."""
        url_lower = url.lower()
        for unreliable in UNRELIABLE_SOURCES:
            if unreliable in url_lower:
                return True
        return False

    def _is_authoritative_source(self, url: str, domain: str) -> bool:
        """Check if URL is from an authoritative source for this domain."""
        url_lower = url.lower()

        # Check domain-specific authoritative sources
        domain_sources = AUTHORITATIVE_SOURCES.get(domain.lower(), [])
        for auth_source in domain_sources:
            if auth_source in url_lower:
                return True

        # Also check .gov and .edu as generally authoritative
        if '.gov' in url_lower or '.edu' in url_lower:
            return True

        return False

    def _check_for_myths(self, content: str) -> Dict[str, Any]:
        """Check content for mythology patterns (unrealistic claims)."""
        result = {
            'has_myths': False,
            'warnings': [],
            'myth_count': 0
        }

        if not content:
            return result

        content_lower = content.lower()

        for pattern in self.NARRATIVE_MYTHS:
            if re.search(pattern, content_lower):
                result['has_myths'] = True
                result['myth_count'] += 1
                result['warnings'].append(f"Detected unrealistic claim pattern")

        return result

    def get_stats(self) -> Dict[str, Any]:
        """Get validation statistics."""
        total = self.validation_stats['total_checks']
        return {
            **self.validation_stats,
            'validation_rate': (
                self.validation_stats['valid_sources'] / max(total, 1)
            ) * 100,
            'myth_detection_rate': (
                self.validation_stats['myth_detections'] / max(total, 1)
            ) * 100
        }


class ShiftVerificationService:
    """
    Service to verify narrative shifts have adequate source corroboration.

    Integrates with NarrativeShift model to:
    1. Track unique source count per shift
    2. Set verified status based on corroboration
    3. Adjust confidence based on source quality
    """

    def __init__(self):
        self.validator = NarrativeMythologyValidator()
        logger.info("🔍 ShiftVerificationService initialized")

    def verify_shift(self, shift_id: str) -> Dict[str, Any]:
        """
        Verify a narrative shift has adequate corroboration.

        Args:
            shift_id: UUID of the NarrativeShift

        Returns:
            Dict with verification results
        """
        from core.models_narrative_drift import NarrativeShift, NarrativeEvidence

        try:
            shift = NarrativeShift.objects.get(id=shift_id)
        except NarrativeShift.DoesNotExist:
            return {'error': f'Shift {shift_id} not found'}

        # Get evidence for this shift's narrative
        evidence = NarrativeEvidence.objects.filter(
            narrative=shift.old_narrative
        )

        # Count unique sources (by domain)
        unique_sources = set()
        authoritative_count = 0

        for e in evidence:
            if e.source_url:
                parsed = urlparse(e.source_url)
                unique_sources.add(parsed.netloc)

                # Check if authoritative
                if self.validator._is_authoritative_source(
                    e.source_url, shift.domain
                ):
                    authoritative_count += 1

        unique_count = len(unique_sources)

        # Validate the shift
        validation = self.validator.validate_shift(
            shift_data={'id': str(shift.id), 'title': shift.old_narrative.title},
            evidence_count=evidence.count(),
            unique_source_count=unique_count
        )

        # Update shift based on validation
        if validation['verified'] and not shift.verified:
            shift.verified = True
            shift.save(update_fields=['verified'])
            logger.info(f"✅ Shift {shift_id[:8]} verified with {unique_count} sources")

        # Adjust confidence if needed
        if validation['confidence_adjustment'] != 0:
            new_confidence = float(shift.confidence) + validation['confidence_adjustment']
            new_confidence = max(0.1, min(0.95, new_confidence))  # Clamp to valid range
            shift.confidence = Decimal(str(new_confidence))
            shift.save(update_fields=['confidence'])

        return {
            'shift_id': str(shift.id),
            'verified': shift.verified,
            'unique_sources': unique_count,
            'authoritative_sources': authoritative_count,
            'total_evidence': evidence.count(),
            'confidence': float(shift.confidence),
            'warnings': validation['warnings']
        }

    def verify_all_unverified_shifts(self, limit: int = 50) -> Dict[str, Any]:
        """Verify all unverified shifts."""
        from core.models_narrative_drift import NarrativeShift

        unverified = NarrativeShift.objects.filter(verified=False)[:limit]

        results = {
            'checked': 0,
            'verified': 0,
            'still_unverified': 0,
            'errors': 0
        }

        for shift in unverified:
            try:
                result = self.verify_shift(str(shift.id))
                results['checked'] += 1

                if result.get('verified'):
                    results['verified'] += 1
                else:
                    results['still_unverified'] += 1

            except Exception as e:
                logger.error(f"Error verifying shift {shift.id}: {e}")
                results['errors'] += 1

        return results


# Global instances
narrative_mythology_validator = NarrativeMythologyValidator()
shift_verification_service = ShiftVerificationService()

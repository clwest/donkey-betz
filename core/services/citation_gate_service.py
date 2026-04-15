"""
Session 846: Citation Gate Service

Validates that critical agent outputs include proper source citations.
Prevents hallucination by requiring evidence-based outputs from Research,
Financial, and Strategy agents.

Citation Requirements:
- Research agents: Minimum 2 sources with URLs
- Financial agents: Minimum 2 sources (at least 1 with data freshness)
- Strategy agents: Minimum 1 source

Enforcement Modes:
- 'strict': Block outputs that fail validation (raise CitationRequiredError)
- 'warn': Log violation but allow output (default)
- 'audit': Only record violation, no warnings
"""

import logging
import re
import uuid
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from django.utils import timezone

logger = logging.getLogger(__name__)


class CitationRequiredError(Exception):
    """Raised when an output fails citation requirements in strict mode."""
    def __init__(self, message: str, violation_type: str, sources_found: int, sources_required: int):
        super().__init__(message)
        self.violation_type = violation_type
        self.sources_found = sources_found
        self.sources_required = sources_required


@dataclass
class CitationRequirement:
    """Defines citation requirements for an agent category."""
    min_sources: int
    require_urls: bool = True
    require_fresh_data: bool = False  # For financial agents
    max_synthetic_ratio: float = 0.5  # Max ratio of synthetic sources allowed
    freshness_hours: int = 72  # How recent data must be


class CitationGateService:
    """
    Validates agent outputs against citation requirements.

    Usage:
        service = CitationGateService()

        # Check if output passes validation
        is_valid, violations = service.validate(
            agent_name='ResearchAgent',
            result={'content': '...', 'sources': [...]},
            task='Research AI trends'
        )

        # Or use with enforcement
        service.enforce(
            agent_name='ResearchAgent',
            result=result,
            mode='strict'  # Will raise CitationRequiredError
        )
    """

    # Agent categories that require citations
    CITATION_REQUIREMENTS: Dict[str, CitationRequirement] = {
        # Research agents - need solid sourcing
        'Research': CitationRequirement(min_sources=2, require_urls=True),
        'Analytics': CitationRequirement(min_sources=2, require_urls=True),

        # Financial agents - need fresh, verified data
        'Finance': CitationRequirement(
            min_sources=2,
            require_urls=True,
            require_fresh_data=True,
            freshness_hours=24
        ),

        # Strategy agents - need some grounding
        'Strategy': CitationRequirement(min_sources=1, require_urls=False),
        'Marketing': CitationRequirement(min_sources=1, require_urls=False),
    }

    # Map agent names to categories (mirrors DeliverableEnvelopeService)
    AGENT_CATEGORY_MAP: Dict[str, str] = {
        # Research
        'ResearchAgent': 'Research',
        'TrendAnalysisAgent': 'Analytics',
        'MarketIntelligenceAgent': 'Analytics',
        'CompetitorAnalysisAgent': 'Analytics',
        'CustomerResearchAgent': 'Research',

        # Financial
        'StockAnalystAgent': 'Finance',
        'StockAuditCoordinator': 'Finance',
        'BullCaseAgent': 'Finance',
        'BearCaseAgent': 'Finance',
        'ValuationAgent': 'Finance',
        'RiskAssessmentAgent': 'Finance',
        'PredictionMarketAnalyst': 'Finance',
        'SportsOddsAnalyst': 'Finance',
        'ArbitrageDetector': 'Finance',
        'SignalScannerAgent': 'Finance',
        'MarketMovementMonitor': 'Finance',
        'MarketAnomalyDetector': 'Finance',

        # Strategy
        'ContentStrategyAgent': 'Strategy',
        'BrandIdentityAgent': 'Strategy',
        'BrandStrategyAgent': 'Strategy',
        'MarketingStrategyAgent': 'Marketing',
        'SEOOptimizerAgent': 'Marketing',
    }

    # Source field names to look for in results
    SOURCE_FIELDS = [
        'sources', 'sources_used', 'references', 'citations',
        'data_sources', 'source_urls', 'bibliography'
    ]

    def __init__(self, default_mode: str = 'warn'):
        """
        Initialize the citation gate.

        Args:
            default_mode: Default enforcement mode ('strict', 'warn', 'audit')
        """
        self.default_mode = default_mode
        self.logger = logging.getLogger(__name__)

    def get_requirement(self, agent_name: str) -> Optional[CitationRequirement]:
        """Get citation requirement for an agent."""
        category = self.AGENT_CATEGORY_MAP.get(agent_name)
        if not category:
            return None
        return self.CITATION_REQUIREMENTS.get(category)

    def requires_citations(self, agent_name: str) -> bool:
        """Check if an agent requires citations."""
        return self.get_requirement(agent_name) is not None

    def validate(
        self,
        agent_name: str,
        result: Dict[str, Any],
        task: str = '',
        trace_id: Optional[uuid.UUID] = None,
    ) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Validate an agent output against citation requirements.

        Args:
            agent_name: Name of the agent that produced the output
            result: The agent result dictionary
            task: The task/prompt given to the agent
            trace_id: Optional trace ID for linking

        Returns:
            Tuple of (is_valid, list of violations)
        """
        requirement = self.get_requirement(agent_name)
        if not requirement:
            # Agent doesn't require citations
            return True, []

        violations = []
        sources = self._extract_sources(result)

        # Check 1: Minimum source count
        if len(sources) < requirement.min_sources:
            violations.append({
                'type': 'insufficient_sources' if sources else 'no_sources',
                'message': f"Required {requirement.min_sources} sources, found {len(sources)}",
                'required': requirement.min_sources,
                'found': len(sources),
            })

        # Check 2: URL requirement
        if requirement.require_urls and sources:
            sources_with_urls = [s for s in sources if self._has_valid_url(s)]
            if len(sources_with_urls) < requirement.min_sources:
                violations.append({
                    'type': 'no_urls',
                    'message': f"Required {requirement.min_sources} sources with URLs, found {len(sources_with_urls)}",
                    'required': requirement.min_sources,
                    'found': len(sources_with_urls),
                })

        # Check 3: Synthetic source ratio
        if sources:
            synthetic_count = len([s for s in sources if self._is_synthetic(s)])
            synthetic_ratio = synthetic_count / len(sources)
            if synthetic_ratio > requirement.max_synthetic_ratio:
                violations.append({
                    'type': 'synthetic_only',
                    'message': f"Too many synthetic sources: {synthetic_count}/{len(sources)} ({synthetic_ratio:.0%})",
                    'synthetic_count': synthetic_count,
                    'total_count': len(sources),
                    'max_ratio': requirement.max_synthetic_ratio,
                })

        # Check 4: Data freshness (for financial agents)
        if requirement.require_fresh_data and sources:
            stale_threshold = timezone.now() - timedelta(hours=requirement.freshness_hours)
            fresh_sources = [s for s in sources if self._is_fresh(s, stale_threshold)]
            if len(fresh_sources) == 0:
                violations.append({
                    'type': 'stale_sources',
                    'message': f"No sources within {requirement.freshness_hours} hours",
                    'freshness_hours': requirement.freshness_hours,
                })

        is_valid = len(violations) == 0
        return is_valid, violations

    def enforce(
        self,
        agent_name: str,
        result: Dict[str, Any],
        task: str = '',
        trace_id: Optional[uuid.UUID] = None,
        execution_id: Optional[uuid.UUID] = None,
        mode: Optional[str] = None,
    ) -> bool:
        """
        Enforce citation requirements with specified mode.

        Args:
            agent_name: Name of the agent
            result: The agent result dictionary
            task: The task/prompt
            trace_id: Optional trace ID
            execution_id: Optional execution ID
            mode: Enforcement mode ('strict', 'warn', 'audit')

        Returns:
            True if output passes validation

        Raises:
            CitationRequiredError: In strict mode when validation fails
        """
        mode = mode or self.default_mode
        is_valid, violations = self.validate(agent_name, result, task, trace_id)

        if is_valid:
            return True

        # Record violations
        sources = self._extract_sources(result)
        requirement = self.get_requirement(agent_name)

        for violation in violations:
            self._record_violation(
                violation_type=violation['type'],
                agent_name=agent_name,
                agent_category=self.AGENT_CATEGORY_MAP.get(agent_name, ''),
                required_sources=requirement.min_sources if requirement else 0,
                provided_sources=len(sources),
                sources_detail=sources[:10],  # Limit stored sources
                task_description=task[:500],
                output_preview=self._get_output_preview(result),
                trace_id=trace_id,
                execution_id=execution_id,
                was_blocked=(mode == 'strict'),
            )

        # Handle based on mode
        if mode == 'strict':
            primary_violation = violations[0]
            raise CitationRequiredError(
                message=f"Citation requirement failed for {agent_name}: {primary_violation['message']}",
                violation_type=primary_violation['type'],
                sources_found=len(sources),
                sources_required=requirement.min_sources if requirement else 0,
            )
        elif mode == 'warn':
            self.logger.warning(
                f"Citation violation for {agent_name}: "
                f"{len(sources)} sources found, {requirement.min_sources if requirement else 0} required. "
                f"Violations: {[v['type'] for v in violations]}"
            )

        return False

    def _extract_sources(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract sources from agent result."""
        sources = []

        # Try known source fields
        for field in self.SOURCE_FIELDS:
            if field in result:
                val = result[field]
                if isinstance(val, list):
                    sources.extend(self._normalize_sources(val))
                elif isinstance(val, dict):
                    sources.extend(self._normalize_sources([val]))

        # Check nested 'data' field
        if 'data' in result and isinstance(result['data'], dict):
            for field in self.SOURCE_FIELDS:
                if field in result['data']:
                    val = result['data'][field]
                    if isinstance(val, list):
                        sources.extend(self._normalize_sources(val))

        # Check for search results format
        if 'results' in result and isinstance(result['results'], list):
            for item in result['results']:
                if isinstance(item, dict) and ('url' in item or 'source' in item):
                    sources.append(self._normalize_source(item))

        # Deduplicate by URL
        seen_urls = set()
        unique_sources = []
        for source in sources:
            url = source.get('url', '')
            if url and url in seen_urls:
                continue
            if url:
                seen_urls.add(url)
            unique_sources.append(source)

        return unique_sources

    def _normalize_sources(self, sources: List) -> List[Dict[str, Any]]:
        """Normalize a list of sources to standard format."""
        normalized = []
        for source in sources:
            normalized.append(self._normalize_source(source))
        return normalized

    def _normalize_source(self, source: Any) -> Dict[str, Any]:
        """Normalize a single source to standard format."""
        if isinstance(source, str):
            # Could be just a URL or description
            if source.startswith('http'):
                return {'url': source, 'type': 'url'}
            return {'description': source, 'type': 'text'}

        if isinstance(source, dict):
            return {
                'url': source.get('url') or source.get('link') or source.get('href', ''),
                'title': source.get('title', ''),
                'source': source.get('source', ''),
                'method': source.get('method', ''),
                'date': source.get('date', ''),
                'type': 'structured',
            }

        return {'value': str(source), 'type': 'unknown'}

    def _has_valid_url(self, source: Dict[str, Any]) -> bool:
        """Check if source has a valid URL."""
        url = source.get('url', '')
        if not url:
            return False
        # Basic URL validation
        return url.startswith('http://') or url.startswith('https://')

    def _is_synthetic(self, source: Dict[str, Any]) -> bool:
        """Check if source is synthetic/mock data."""
        method = source.get('method', '').lower()
        source_name = source.get('source', '').lower()

        synthetic_indicators = [
            'synthetic', 'mock', 'fallback', 'placeholder',
            'example.com', 'test', 'demo'
        ]

        for indicator in synthetic_indicators:
            if indicator in method or indicator in source_name:
                return True

        url = source.get('url', '').lower()
        if 'example.com' in url or 'test.com' in url:
            return True

        return False

    def _is_fresh(self, source: Dict[str, Any], threshold: datetime) -> bool:
        """Check if source data is fresh enough."""
        date_str = source.get('date', '')
        if not date_str:
            # No date = assume not fresh for strict checking
            return False

        try:
            # Try common date formats
            for fmt in ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S']:
                try:
                    source_date = datetime.strptime(date_str[:19], fmt)
                    if timezone.is_naive(source_date):
                        source_date = timezone.make_aware(source_date)
                    return source_date >= threshold
                except ValueError:
                    continue
        except Exception as _e:
            logger.warning(
                "citation_gate_service._is_fresh: swallowed (%s: %s) — degraded",
                type(_e).__name__, _e,
            )

        return False

    def _get_output_preview(self, result: Dict[str, Any]) -> str:
        """Get a preview of the output for logging."""
        content_keys = ['content', 'output', 'result', 'text', 'analysis']
        for key in content_keys:
            if key in result and isinstance(result[key], str):
                return result[key][:500]
        return str(result)[:500]

    def _record_violation(
        self,
        violation_type: str,
        agent_name: str,
        agent_category: str,
        required_sources: int,
        provided_sources: int,
        sources_detail: List[Dict],
        task_description: str,
        output_preview: str,
        trace_id: Optional[uuid.UUID],
        execution_id: Optional[uuid.UUID],
        was_blocked: bool,
    ):
        """Record a citation violation to the database."""
        try:
            from core.models_orchestration import CitationViolation

            CitationViolation.objects.create(
                violation_type=violation_type,
                agent_name=agent_name,
                agent_category=agent_category,
                required_sources=required_sources,
                provided_sources=provided_sources,
                sources_detail=sources_detail,
                task_description=task_description,
                output_preview=output_preview,
                trace_id=trace_id,
                execution_id=execution_id,
                was_blocked=was_blocked,
            )
        except Exception as e:
            self.logger.warning(f"Failed to record citation violation: {e}")


# Singleton instance for easy access
_service_instance: Optional[CitationGateService] = None


def get_citation_gate_service(default_mode: str = 'warn') -> CitationGateService:
    """Get or create the singleton CitationGateService instance."""
    global _service_instance
    if _service_instance is None:
        _service_instance = CitationGateService(default_mode=default_mode)
    return _service_instance

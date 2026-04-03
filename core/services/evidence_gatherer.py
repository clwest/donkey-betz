"""
Session 856: Evidence Gatherer

Collects evidence from multiple sources to diagnose failures.
Stops gathering when confidence threshold is reached.

Evidence Priority (stops at 80% confidence):
1. Raw exception/status code
2. Provider/endpoint info
3. Rate-limit metadata
4. Recent system events
5. LLM synthesis (last resort)
"""

import logging
from typing import Dict, Any, List, Optional
from django.utils import timezone

logger = logging.getLogger(__name__)


class EvidenceGatherer:
    """
    Gathers evidence from multiple sources to diagnose failures.

    Uses a priority-based approach, stopping when confidence
    threshold is reached to avoid unnecessary LLM calls.
    """

    # Evidence source weights for confidence calculation
    SOURCE_WEIGHTS = {
        'exception': 0.4,       # Exception info is highly reliable
        'provider': 0.3,        # Provider metadata is trustworthy
        'rate_limit': 0.5,      # Rate limit info is definitive
        'system_event': 0.2,    # System events provide context
        'pattern_match': 0.3,   # Pattern matching from templates
        'llm_synthesis': 0.2,   # LLM synthesis adds nuance but less reliable
    }

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def gather_evidence(
        self,
        signature: 'FailureSignature',
        detections: List['FailureDetection'],
        confidence_threshold: float = 0.8
    ) -> Dict[str, Any]:
        """
        Gather evidence from multiple sources until confidence threshold is met.

        Args:
            signature: The failure signature being diagnosed
            detections: List of detection samples to analyze
            confidence_threshold: Stop gathering when this confidence is reached

        Returns:
            Dict with root_cause, confidence, sources_used, details, affected_components
        """
        self.logger.info(
            f"[Session 856] Gathering evidence for {signature.signature} "
            f"({len(detections)} samples)"
        )

        evidence = {
            'root_cause': '',
            'confidence': 0.0,
            'sources_used': [],
            'details': {},
            'affected_components': [],
        }

        # Phase 1: Exception analysis (highest priority)
        exception_evidence = self._analyze_exceptions(detections)
        if exception_evidence:
            evidence['details']['exception'] = exception_evidence
            evidence['sources_used'].append('exception')
            evidence['confidence'] += self._calculate_source_confidence(
                'exception', exception_evidence
            )

            if evidence['confidence'] >= confidence_threshold:
                evidence['root_cause'] = self._synthesize_root_cause(evidence)
                return evidence

        # Phase 2: Provider analysis
        provider_evidence = self._analyze_provider(signature, detections)
        if provider_evidence:
            evidence['details']['provider'] = provider_evidence
            evidence['sources_used'].append('provider')
            evidence['confidence'] += self._calculate_source_confidence(
                'provider', provider_evidence
            )

            if evidence['confidence'] >= confidence_threshold:
                evidence['root_cause'] = self._synthesize_root_cause(evidence)
                return evidence

        # Phase 3: Rate limit analysis
        rate_limit_evidence = self._analyze_rate_limits(detections)
        if rate_limit_evidence:
            evidence['details']['rate_limit'] = rate_limit_evidence
            evidence['sources_used'].append('rate_limit')
            evidence['confidence'] += self._calculate_source_confidence(
                'rate_limit', rate_limit_evidence
            )

            if evidence['confidence'] >= confidence_threshold:
                evidence['root_cause'] = self._synthesize_root_cause(evidence)
                return evidence

        # Phase 4: System event correlation
        system_evidence = self._analyze_system_events(signature, detections)
        if system_evidence:
            evidence['details']['system_event'] = system_evidence
            evidence['sources_used'].append('system_event')
            evidence['confidence'] += self._calculate_source_confidence(
                'system_event', system_evidence
            )

            if evidence['confidence'] >= confidence_threshold:
                evidence['root_cause'] = self._synthesize_root_cause(evidence)
                return evidence

        # Phase 5: Pattern matching
        pattern_evidence = self._analyze_patterns(signature, detections)
        if pattern_evidence:
            evidence['details']['pattern_match'] = pattern_evidence
            evidence['sources_used'].append('pattern_match')
            evidence['confidence'] += self._calculate_source_confidence(
                'pattern_match', pattern_evidence
            )

            if evidence['confidence'] >= confidence_threshold:
                evidence['root_cause'] = self._synthesize_root_cause(evidence)
                return evidence

        # Phase 6: LLM synthesis (last resort)
        # Only use if confidence is still below threshold
        if evidence['confidence'] < confidence_threshold * 0.5:
            llm_evidence = self._synthesize_with_llm(signature, detections, evidence)
            if llm_evidence:
                evidence['details']['llm_synthesis'] = llm_evidence
                evidence['sources_used'].append('llm_synthesis')
                evidence['confidence'] += self._calculate_source_confidence(
                    'llm_synthesis', llm_evidence
                )

        # Collect affected components
        evidence['affected_components'] = self._extract_affected_components(detections)

        # Final synthesis
        evidence['root_cause'] = self._synthesize_root_cause(evidence)

        # Cap confidence at 1.0
        evidence['confidence'] = min(evidence['confidence'], 1.0)

        self.logger.info(
            f"[Session 856] Evidence gathered: {evidence['confidence']:.0%} confidence "
            f"from {evidence['sources_used']}"
        )

        return evidence

    def _analyze_exceptions(self, detections: List['FailureDetection']) -> Optional[Dict]:
        """Analyze exception patterns from detections."""
        if not detections:
            return None

        # Collect unique error codes and messages
        error_codes = {}
        error_patterns = {}
        stack_patterns = []

        for detection in detections:
            # Count error codes
            if detection.error_code:
                error_codes[detection.error_code] = error_codes.get(
                    detection.error_code, 0
                ) + 1

            # Extract error pattern (first line of error)
            msg_line = detection.error_message.split('\n')[0][:200]
            error_patterns[msg_line] = error_patterns.get(msg_line, 0) + 1

            # Check for common exception classes in stack trace
            if detection.stack_trace:
                for exc_class in ['ValueError', 'TypeError', 'KeyError',
                                  'AttributeError', 'ConnectionError',
                                  'TimeoutError', 'HTTPError']:
                    if exc_class in detection.stack_trace:
                        stack_patterns.append(exc_class)

        # Find most common patterns
        most_common_code = max(error_codes.items(), key=lambda x: x[1])[0] if error_codes else None
        most_common_pattern = max(error_patterns.items(), key=lambda x: x[1])[0] if error_patterns else None

        return {
            'error_codes': error_codes,
            'most_common_code': most_common_code,
            'most_common_pattern': most_common_pattern,
            'exception_classes': list(set(stack_patterns)),
            'sample_count': len(detections),
        }

    def _analyze_provider(
        self,
        signature: 'FailureSignature',
        detections: List['FailureDetection']
    ) -> Optional[Dict]:
        """Analyze provider-specific information."""
        if not signature.provider:
            return None

        # Collect provider context from detections
        models_used = {}
        endpoints = {}

        for detection in detections:
            ctx = detection.context_snapshot or {}

            if ctx.get('model'):
                models_used[ctx['model']] = models_used.get(ctx['model'], 0) + 1

            if ctx.get('endpoint'):
                endpoints[ctx['endpoint']] = endpoints.get(ctx['endpoint'], 0) + 1

        # Get provider health
        from core.services.provider_health_tracker import get_provider_health_tracker
        tracker = get_provider_health_tracker()
        provider_health = {
            'error_count': tracker.get_error_count(signature.provider),
            'is_degraded': tracker.is_provider_degraded(signature.provider),
        }

        return {
            'provider': signature.provider,
            'models_used': models_used,
            'endpoints': endpoints,
            'provider_health': provider_health,
        }

    def _analyze_rate_limits(self, detections: List['FailureDetection']) -> Optional[Dict]:
        """Analyze rate limit patterns."""
        rate_limit_detections = [
            d for d in detections
            if d.error_code == '429' or 'rate' in d.error_message.lower()
        ]

        if not rate_limit_detections:
            return None

        # Analyze timing patterns
        times = [d.detected_at for d in rate_limit_detections]
        if len(times) >= 2:
            times.sort()
            intervals = [
                (times[i+1] - times[i]).total_seconds()
                for i in range(len(times) - 1)
            ]
            avg_interval = sum(intervals) / len(intervals) if intervals else 0
        else:
            avg_interval = 0

        return {
            'rate_limit_count': len(rate_limit_detections),
            'avg_interval_seconds': avg_interval,
            'burst_detected': avg_interval < 60,  # Multiple within 1 minute
        }

    def _analyze_system_events(
        self,
        signature: 'FailureSignature',
        detections: List['FailureDetection']
    ) -> Optional[Dict]:
        """Correlate with recent system events."""
        # Get time range of detections
        if not detections:
            return None

        first_detection = min(d.detected_at for d in detections)
        last_detection = max(d.detected_at for d in detections)

        # Look for correlated events
        events = []

        # Check experiment halts in this time range
        try:
            from core.models_pilot_readiness import Experiment
            experiment_halts = Experiment.objects.filter(
                status='halted',
                halted_at__gte=first_detection,
                halted_at__lte=last_detection
            ).count()
            if experiment_halts > 0:
                events.append(f"{experiment_halts} experiments halted")
        except Exception:
            pass

        # Check agent execution failures
        try:
            from core.models_unified_system import AgentExecution
            exec_failures = AgentExecution.objects.filter(
                status='failed',
                created_at__gte=first_detection,
                created_at__lte=last_detection
            ).count()
            if exec_failures > 0:
                events.append(f"{exec_failures} agent executions failed")
        except Exception:
            pass

        if not events:
            return None

        return {
            'time_range': {
                'from': first_detection.isoformat(),
                'to': last_detection.isoformat(),
            },
            'correlated_events': events,
        }

    def _analyze_patterns(
        self,
        signature: 'FailureSignature',
        detections: List['FailureDetection']
    ) -> Optional[Dict]:
        """Match against known failure patterns."""
        # Known patterns and their root causes
        known_patterns = {
            'OPENAI_429': {
                'root_cause': 'OpenAI API rate limit exceeded',
                'solution_hint': 'Implement exponential backoff or reduce request frequency',
            },
            'ANTHROPIC_429': {
                'root_cause': 'Anthropic API rate limit exceeded',
                'solution_hint': 'Implement exponential backoff or reduce request frequency',
            },
            'TIMEOUT': {
                'root_cause': 'API request timeout',
                'solution_hint': 'Increase timeout threshold or implement retry logic',
            },
            'CONNECTION': {
                'root_cause': 'Network connectivity issue',
                'solution_hint': 'Check network configuration and service availability',
            },
            'AUTH': {
                'root_cause': 'Authentication failure',
                'solution_hint': 'Verify API keys and credentials are valid',
            },
            'CONTEXT_LENGTH': {
                'root_cause': 'Input exceeds model context window',
                'solution_hint': 'Implement chunking or summarization for long inputs',
            },
        }

        # Check for matching patterns
        sig = signature.signature.upper()
        for pattern, info in known_patterns.items():
            if pattern in sig:
                return {
                    'matched_pattern': pattern,
                    'known_root_cause': info['root_cause'],
                    'solution_hint': info['solution_hint'],
                }

        return None

    def _synthesize_with_llm(
        self,
        signature: 'FailureSignature',
        detections: List['FailureDetection'],
        existing_evidence: Dict
    ) -> Optional[Dict]:
        """Use LLM to synthesize evidence (last resort)."""
        # Only use LLM if we really need it
        if existing_evidence['confidence'] >= 0.6:
            return None

        try:
            from openai import OpenAI
            from django.conf import settings

            client = OpenAI(api_key=settings.OPENAI_API_KEY)

            # Build context for LLM
            sample_errors = [d.error_message[:200] for d in detections[:3]]

            prompt = f"""Analyze this failure signature and determine the root cause.

Signature: {signature.signature}
Category: {signature.category}
Provider: {signature.provider or 'N/A'}
Error Code: {signature.error_code or 'N/A'}
Occurrence Count: {signature.occurrence_count}

Sample Error Messages:
{chr(10).join(f'- {e}' for e in sample_errors)}

Existing Evidence:
{existing_evidence.get('details', {})}

Provide a brief root cause analysis (2-3 sentences) and confidence level (0.0-1.0).
Format: ROOT_CAUSE: <analysis> | CONFIDENCE: <0.0-1.0>"""

            response = client.chat.completions.create(
                model="gpt-5-mini",
                messages=[{"role": "user", "content": prompt}],
                max_completion_tokens=200,
            )

            result = response.choices[0].message.content

            # Parse response
            if 'ROOT_CAUSE:' in result and 'CONFIDENCE:' in result:
                parts = result.split('|')
                root_cause = parts[0].replace('ROOT_CAUSE:', '').strip()
                conf_str = parts[1].replace('CONFIDENCE:', '').strip()
                try:
                    confidence = float(conf_str)
                except ValueError:
                    confidence = 0.5

                return {
                    'llm_analysis': root_cause,
                    'llm_confidence': confidence,
                }

        except Exception as e:
            self.logger.warning(f"[Session 856] LLM synthesis failed: {e}")

        return None

    def _calculate_source_confidence(self, source: str, evidence: Dict) -> float:
        """Calculate confidence contribution from a source."""
        base_weight = self.SOURCE_WEIGHTS.get(source, 0.1)

        # Adjust based on evidence quality
        if source == 'exception':
            # Higher confidence if error codes are consistent
            if evidence.get('error_codes'):
                codes = evidence['error_codes']
                if len(codes) == 1:  # All same error code
                    return base_weight * 1.5
        elif source == 'rate_limit':
            if evidence.get('rate_limit_count', 0) >= 5:
                return base_weight * 1.2  # Strong signal
        elif source == 'pattern_match':
            return base_weight * 1.0  # Known pattern is reliable

        return base_weight

    def _synthesize_root_cause(self, evidence: Dict) -> str:
        """Synthesize a root cause explanation from all evidence."""
        parts = []

        details = evidence.get('details', {})

        # Start with pattern match if available (most definitive)
        if 'pattern_match' in details:
            pm = details['pattern_match']
            parts.append(pm.get('known_root_cause', ''))

        # Add exception analysis
        if 'exception' in details:
            exc = details['exception']
            if exc.get('most_common_code'):
                parts.append(f"Error code {exc['most_common_code']} occurred {exc.get('sample_count', 0)} times.")

        # Add provider info
        if 'provider' in details:
            prov = details['provider']
            if prov.get('provider_health', {}).get('is_degraded'):
                parts.append(f"Provider {prov['provider']} is currently degraded.")

        # Add rate limit info
        if 'rate_limit' in details:
            rl = details['rate_limit']
            parts.append(f"Rate limiting detected: {rl.get('rate_limit_count', 0)} occurrences.")
            if rl.get('burst_detected'):
                parts.append("Request bursting pattern detected.")

        # Add LLM synthesis
        if 'llm_synthesis' in details:
            llm = details['llm_synthesis']
            parts.append(llm.get('llm_analysis', ''))

        # Combine
        root_cause = ' '.join(filter(None, parts))

        if not root_cause:
            root_cause = f"Failure signature {evidence.get('signature', 'unknown')} - insufficient evidence for definitive root cause."

        return root_cause[:1000]  # Cap length

    def _extract_affected_components(self, detections: List['FailureDetection']) -> List[str]:
        """Extract list of affected components from detections."""
        components = set()

        for detection in detections:
            if detection.source_name:
                components.add(detection.source_name)

            ctx = detection.context_snapshot or {}
            if ctx.get('agent_name'):
                components.add(ctx['agent_name'])
            if ctx.get('spider_name'):
                components.add(ctx['spider_name'])

        return list(components)[:20]  # Cap at 20


# Singleton instance
_gatherer_instance: Optional[EvidenceGatherer] = None


def get_evidence_gatherer() -> EvidenceGatherer:
    """Get the singleton EvidenceGatherer instance."""
    global _gatherer_instance
    if _gatherer_instance is None:
        _gatherer_instance = EvidenceGatherer()
    return _gatherer_instance

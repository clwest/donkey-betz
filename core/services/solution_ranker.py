"""
Session 856: Solution Ranker

Generates and ranks solutions for diagnosed failures.
Solutions are organized by scope:
- Immediate: Stop the bleeding (quick fixes)
- Structural: Prevent recurrence (code/config changes)
- Observability: Make obvious (monitoring/alerting)
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class SolutionRanker:
    """
    Generates and ranks solutions based on diagnosis data.

    Uses templates for common failure types and LLM for novel cases.
    """

    # Solution templates by signature pattern
    SOLUTION_TEMPLATES = {
        # Rate limit solutions
        'RATE_LIMIT': {
            'immediate': {
                'title': 'Implement exponential backoff retry',
                'description': 'Add retry logic with exponential backoff to handle transient rate limits',
                'impact': 'high',
                'effort': 'small',
                'confidence': 0.9,
                'steps': [
                    'Add tenacity or backoff decorator to API calls',
                    'Configure initial delay of 1s, max delay of 60s',
                    'Set max retries to 5',
                ],
                'files': ['core/services/llm_client.py'],
                'success_criteria': 'Rate limit errors retried successfully without user impact',
            },
            'structural': {
                'title': 'Implement request queue with rate limiting',
                'description': 'Add a request queue that respects provider rate limits proactively',
                'impact': 'high',
                'effort': 'medium',
                'confidence': 0.85,
                'steps': [
                    'Create RateLimitedQueue class',
                    'Track requests per minute per provider',
                    'Delay requests when approaching limit',
                    'Add provider-specific configuration',
                ],
                'files': ['core/services/llm_client.py', 'core/services/request_queue.py'],
                'success_criteria': 'Rate limit errors reduced by 90%',
            },
            'observability': {
                'title': 'Add rate limit monitoring dashboard',
                'description': 'Track rate limit hits per provider and alert on elevated rates',
                'impact': 'medium',
                'effort': 'small',
                'confidence': 0.95,
                'steps': [
                    'Add rate_limit_hits metric to provider health tracker',
                    'Create dashboard panel for rate limit trends',
                    'Configure alert for >10 rate limits in 5 minutes',
                ],
                'files': ['core/services/provider_health_tracker.py'],
                'success_criteria': 'Proactive alerts before rate limit issues impact users',
            },
        },

        # Timeout solutions
        'TIMEOUT': {
            'immediate': {
                'title': 'Increase timeout threshold',
                'description': 'Increase API timeout to handle slow responses',
                'impact': 'medium',
                'effort': 'trivial',
                'confidence': 0.8,
                'steps': [
                    'Locate timeout configuration',
                    'Increase from current value to 120s',
                    'Test with slow providers',
                ],
                'files': ['core/services/llm_client.py'],
                'success_criteria': 'Timeout errors reduced by 50%',
            },
            'structural': {
                'title': 'Implement async request handling',
                'description': 'Make LLM calls async to avoid blocking and handle timeouts gracefully',
                'impact': 'high',
                'effort': 'large',
                'confidence': 0.7,
                'steps': [
                    'Convert synchronous calls to async',
                    'Add proper timeout handling',
                    'Implement task cancellation on timeout',
                    'Add fallback to faster model on timeout',
                ],
                'files': ['core/services/llm_client.py', 'core/agents/base_agent.py'],
                'success_criteria': 'Timeout handling is graceful, user experience preserved',
            },
            'observability': {
                'title': 'Add latency tracking per provider',
                'description': 'Track and alert on provider latency to detect slowdowns early',
                'impact': 'medium',
                'effort': 'small',
                'confidence': 0.9,
                'steps': [
                    'Add latency_ms metric to API calls',
                    'Track p50, p95, p99 latency per provider',
                    'Alert when p95 exceeds 30s',
                ],
                'files': ['core/services/provider_health_tracker.py'],
                'success_criteria': 'Early warning of provider slowdowns',
            },
        },

        # Authentication solutions
        'AUTH': {
            'immediate': {
                'title': 'Verify and rotate API keys',
                'description': 'Check API key validity and rotate if expired',
                'impact': 'high',
                'effort': 'trivial',
                'confidence': 0.95,
                'steps': [
                    'Verify API key in provider dashboard',
                    'Generate new API key if invalid',
                    'Update in .env and restart services',
                ],
                'files': ['.env'],
                'commands': ['make restart'],
                'success_criteria': 'Authentication succeeds with valid key',
            },
            'structural': {
                'title': 'Implement credential rotation automation',
                'description': 'Automate API key rotation and validation',
                'impact': 'medium',
                'effort': 'medium',
                'confidence': 0.7,
                'steps': [
                    'Add credential validation on startup',
                    'Implement key rotation script',
                    'Add expiry tracking and alerts',
                ],
                'files': ['core/services/credential_manager.py'],
                'success_criteria': 'Automatic detection and alerting on credential issues',
            },
            'observability': {
                'title': 'Add auth failure alerting',
                'description': 'Alert immediately on authentication failures',
                'impact': 'medium',
                'effort': 'trivial',
                'confidence': 0.95,
                'steps': [
                    'Add auth_failure counter metric',
                    'Configure immediate alert on any auth failure',
                ],
                'files': ['core/services/provider_health_tracker.py'],
                'success_criteria': 'Immediate notification on auth failures',
            },
        },

        # Connection error solutions
        'CONNECTION': {
            'immediate': {
                'title': 'Retry connection with backoff',
                'description': 'Add retry logic for transient connection failures',
                'impact': 'high',
                'effort': 'small',
                'confidence': 0.85,
                'steps': [
                    'Wrap connection code with retry decorator',
                    'Configure exponential backoff',
                    'Add connection pooling if not present',
                ],
                'files': ['core/services/llm_client.py'],
                'success_criteria': 'Transient connection failures auto-recovered',
            },
            'structural': {
                'title': 'Implement circuit breaker pattern',
                'description': 'Add circuit breaker to prevent cascade failures',
                'impact': 'high',
                'effort': 'medium',
                'confidence': 0.8,
                'steps': [
                    'Install pybreaker or implement custom circuit breaker',
                    'Configure per-provider circuit breakers',
                    'Add fallback behavior when circuit is open',
                ],
                'files': ['core/services/llm_client.py', 'core/services/circuit_breaker.py'],
                'success_criteria': 'System degrades gracefully during provider outages',
            },
            'observability': {
                'title': 'Add connection health monitoring',
                'description': 'Monitor connection success rates and alert on degradation',
                'impact': 'medium',
                'effort': 'small',
                'confidence': 0.9,
                'steps': [
                    'Track connection_success and connection_failure metrics',
                    'Calculate success rate per provider',
                    'Alert when success rate drops below 95%',
                ],
                'files': ['core/services/provider_health_tracker.py'],
                'success_criteria': 'Early warning of connectivity issues',
            },
        },

        # Server error solutions
        'SERVER': {
            'immediate': {
                'title': 'Implement automatic retry with fallback',
                'description': 'Retry on 5xx errors with fallback to alternate provider',
                'impact': 'high',
                'effort': 'small',
                'confidence': 0.85,
                'steps': [
                    'Add retry decorator for 5xx errors',
                    'Configure fallback provider order',
                    'Log which provider served request',
                ],
                'files': ['core/services/llm_client.py'],
                'success_criteria': 'Server errors auto-recovered via retry or fallback',
            },
            'structural': {
                'title': 'Implement multi-provider load balancing',
                'description': 'Distribute load across providers based on health',
                'impact': 'high',
                'effort': 'large',
                'confidence': 0.75,
                'steps': [
                    'Create ProviderLoadBalancer service',
                    'Track health score per provider',
                    'Route requests to healthiest provider',
                    'Implement weighted round-robin',
                ],
                'files': ['core/services/provider_load_balancer.py'],
                'success_criteria': 'Automatic load distribution based on provider health',
            },
            'observability': {
                'title': 'Add provider error rate dashboard',
                'description': 'Track and visualize error rates per provider',
                'impact': 'medium',
                'effort': 'small',
                'confidence': 0.9,
                'steps': [
                    'Enhance provider_health_tracker with error rate calculation',
                    'Create dashboard showing error rates over time',
                    'Add alert for sustained elevated error rates',
                ],
                'files': ['core/services/provider_health_tracker.py'],
                'success_criteria': 'Visibility into provider error patterns',
            },
        },

        # Context length solutions
        'CONTEXT_LENGTH': {
            'immediate': {
                'title': 'Truncate long inputs',
                'description': 'Automatically truncate inputs that exceed context window',
                'impact': 'medium',
                'effort': 'trivial',
                'confidence': 0.9,
                'steps': [
                    'Add input length check before API call',
                    'Truncate to model max tokens minus buffer',
                    'Log when truncation occurs',
                ],
                'files': ['core/services/llm_client.py'],
                'success_criteria': 'Context length errors eliminated',
            },
            'structural': {
                'title': 'Implement smart chunking',
                'description': 'Split long documents into semantic chunks',
                'impact': 'high',
                'effort': 'medium',
                'confidence': 0.8,
                'steps': [
                    'Add document chunking service',
                    'Use sentence boundaries for splits',
                    'Implement map-reduce for long documents',
                ],
                'files': ['core/services/document_chunker.py'],
                'success_criteria': 'Long documents processed correctly via chunking',
            },
            'observability': {
                'title': 'Track input token usage',
                'description': 'Monitor input sizes to identify problematic patterns',
                'impact': 'low',
                'effort': 'trivial',
                'confidence': 0.95,
                'steps': [
                    'Log input token count per request',
                    'Track distribution of input sizes',
                    'Alert on requests approaching context limit',
                ],
                'files': ['core/services/llm_client.py'],
                'success_criteria': 'Visibility into token usage patterns',
            },
        },
    }

    # Default solutions for unknown patterns
    DEFAULT_SOLUTIONS = {
        'immediate': {
            'title': 'Add error handling and retry',
            'description': 'Add generic error handling with retry logic',
            'impact': 'medium',
            'effort': 'small',
            'confidence': 0.5,
            'steps': [
                'Identify the failing code path',
                'Add try/except with appropriate exception handling',
                'Implement retry with exponential backoff',
            ],
            'success_criteria': 'Error is handled gracefully with retries',
        },
        'structural': {
            'title': 'Investigate root cause and implement fix',
            'description': 'Deep investigation required - root cause unclear',
            'impact': 'medium',
            'effort': 'medium',
            'confidence': 0.3,
            'steps': [
                'Review stack traces and error logs',
                'Reproduce the issue locally',
                'Identify root cause and implement fix',
                'Add test coverage for the scenario',
            ],
            'success_criteria': 'Root cause identified and permanently fixed',
        },
        'observability': {
            'title': 'Add detailed logging for this error type',
            'description': 'Improve logging to better diagnose future occurrences',
            'impact': 'medium',
            'effort': 'small',
            'confidence': 0.8,
            'steps': [
                'Add structured logging around the error point',
                'Include relevant context in log messages',
                'Set up log-based alerting',
            ],
            'success_criteria': 'Future occurrences are easier to diagnose',
        },
    }

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def generate_solutions(
        self,
        diagnosis: 'FailureDiagnosis'
    ) -> List[Dict[str, Any]]:
        """
        Generate ranked solutions for a diagnosis.

        Args:
            diagnosis: The FailureDiagnosis to generate solutions for

        Returns:
            List of solution dicts sorted by priority
        """
        self.logger.info(
            f"[Session 856] Generating solutions for {diagnosis.signature.signature}"
        )

        solutions = []
        signature = diagnosis.signature.signature.upper()

        # Find matching template
        template = None
        for pattern, t in self.SOLUTION_TEMPLATES.items():
            if pattern in signature:
                template = t
                break

        # Use default template if no match
        if not template:
            template = self.DEFAULT_SOLUTIONS
            self.logger.info(
                f"[Session 856] Using default solutions for {signature}"
            )

        # Generate solutions for each scope
        for scope in ['immediate', 'structural', 'observability']:
            if scope in template:
                solution = self._create_solution(template[scope], scope, diagnosis)
                solutions.append(solution)

        # Sort by priority (impact * confidence / effort)
        solutions = self._rank_solutions(solutions)

        self.logger.info(
            f"[Session 856] Generated {len(solutions)} solutions"
        )

        return solutions

    def _create_solution(
        self,
        template: Dict[str, Any],
        scope: str,
        diagnosis: 'FailureDiagnosis'
    ) -> Dict[str, Any]:
        """Create a solution from a template."""
        # Customize template based on diagnosis
        solution = {
            'title': template.get('title', 'Fix the issue'),
            'description': template.get('description', ''),
            'scope': scope,
            'impact': template.get('impact', 'medium'),
            'effort': template.get('effort', 'small'),
            'confidence': template.get('confidence', 0.5),
            'steps': template.get('steps', []),
            'files': template.get('files', []),
            'commands': template.get('commands', []),
            'success_criteria': template.get('success_criteria', ''),
            'verification': [],
        }

        # Add verification steps based on success criteria
        if solution['success_criteria']:
            solution['verification'] = [
                f"Verify: {solution['success_criteria']}",
                'Run tests to confirm fix',
                'Monitor for recurrence',
            ]

        # Adjust confidence based on diagnosis confidence
        solution['confidence'] = min(
            solution['confidence'],
            diagnosis.root_cause_confidence * 1.1  # Slightly boost since we have a diagnosis
        )

        return solution

    def _rank_solutions(self, solutions: List[Dict]) -> List[Dict]:
        """Rank solutions by priority score."""
        impact_weights = {'high': 3.0, 'medium': 2.0, 'low': 1.0}
        effort_weights = {'trivial': 1.0, 'small': 2.0, 'medium': 3.0, 'large': 4.0}

        for solution in solutions:
            impact_w = impact_weights.get(solution['impact'], 2.0)
            effort_w = effort_weights.get(solution['effort'], 2.0)
            solution['priority_score'] = (
                impact_w * solution['confidence']
            ) / effort_w

        # Sort by priority score descending
        return sorted(solutions, key=lambda x: x['priority_score'], reverse=True)

    def get_solution_for_scope(
        self,
        diagnosis: 'FailureDiagnosis',
        scope: str
    ) -> Optional[Dict[str, Any]]:
        """Get a single solution for a specific scope."""
        solutions = self.generate_solutions(diagnosis)
        for solution in solutions:
            if solution['scope'] == scope:
                return solution
        return None


# Singleton instance
_ranker_instance: Optional[SolutionRanker] = None


def get_solution_ranker() -> SolutionRanker:
    """Get the singleton SolutionRanker instance."""
    global _ranker_instance
    if _ranker_instance is None:
        _ranker_instance = SolutionRanker()
    return _ranker_instance

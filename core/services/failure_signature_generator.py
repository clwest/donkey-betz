"""
Session 856: Failure Signature Generator

Generates stable signatures from error messages and context.
These signatures group related failures together for diagnosis.

Examples:
- OPENAI_429_QUOTA -> OpenAI rate limit errors
- TIMEOUT_PROVIDER_ANTHROPIC -> Anthropic API timeouts
- DATA_ERROR_MISSING_FIELD -> Missing required field errors
- EXECUTION_ERROR_AGENT_ResearchAgent -> Agent execution failures
"""

import hashlib
import logging
import re
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)


class FailureSignatureGenerator:
    """
    Generates stable, deterministic signatures from error data.

    Signatures are used to group related failures for diagnosis,
    even when error messages contain unique IDs or timestamps.
    """

    # Patterns to strip from error messages (UUIDs, timestamps, etc.)
    NORMALIZATION_PATTERNS = [
        # UUIDs
        (r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '<UUID>'),
        # ISO timestamps
        (r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?', '<TIMESTAMP>'),
        # Unix timestamps
        (r'\b\d{10,13}\b', '<UNIX_TS>'),
        # IP addresses
        (r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', '<IP>'),
        # Memory addresses
        (r'0x[0-9a-fA-F]+', '<ADDR>'),
        # File paths with dynamic parts
        (r'/tmp/[^\s]+', '/tmp/<TEMP>'),
        # Request IDs
        (r'request[_-]?id[=:]\s*[a-zA-Z0-9_-]+', 'request_id=<ID>'),
        # Task IDs
        (r'task[_-]?id[=:]\s*[a-zA-Z0-9_-]+', 'task_id=<ID>'),
        # Session IDs
        (r'session[_-]?id[=:]\s*[a-zA-Z0-9_-]+', 'session_id=<ID>'),
    ]

    # Provider error code patterns
    PROVIDER_PATTERNS = {
        'openai': {
            'rate_limit': [
                r'rate.*limit', r'429', r'quota.*exceeded', r'too.*many.*requests',
                r'RateLimitError', r'insufficient_quota'
            ],
            'auth': [r'401', r'invalid.*api.*key', r'authentication', r'AuthenticationError'],
            'server': [r'500', r'502', r'503', r'504', r'InternalServerError'],
            'timeout': [r'timeout', r'timed.*out', r'TimeoutError'],
            'context_length': [r'context.*length', r'maximum.*context', r'token.*limit'],
            'content_filter': [r'content.*filter', r'content.*policy', r'flagged'],
        },
        'anthropic': {
            'rate_limit': [r'rate.*limit', r'429', r'overloaded'],
            'auth': [r'401', r'invalid.*api.*key', r'authentication'],
            'server': [r'500', r'502', r'503', r'504', r'overloaded'],
            'timeout': [r'timeout', r'timed.*out'],
        },
        'deepseek': {
            'rate_limit': [r'rate.*limit', r'429'],
            'auth': [r'401', r'invalid.*api.*key'],
            'server': [r'500', r'502', r'503', r'504'],
            'timeout': [r'timeout', r'timed.*out'],
        },
        'gemini': {
            'rate_limit': [r'429', r'RESOURCE_EXHAUSTED', r'quota'],
            'auth': [r'401', r'API_KEY_INVALID'],
            'server': [r'500', r'INTERNAL'],
            'timeout': [r'DEADLINE_EXCEEDED', r'timeout'],
        },
        'ollama': {
            'connection': [r'connection.*refused', r'ECONNREFUSED'],
            'timeout': [r'timeout', r'timed.*out'],
            'model': [r'model.*not.*found', r'pull.*model'],
        },
        'together': {
            'rate_limit': [r'429', r'rate.*limit'],
            'auth': [r'401', r'unauthorized'],
            'server': [r'500', r'502', r'503', r'504'],
            'timeout': [r'timeout'],
        },
    }

    # Category detection patterns
    CATEGORY_PATTERNS = {
        'provider_error': [
            r'openai', r'anthropic', r'deepseek', r'gemini', r'ollama', r'together',
            r'api.*error', r'APIError', r'completion.*error'
        ],
        'timeout': [r'timeout', r'timed.*out', r'TimeoutError', r'deadline'],
        'data_error': [
            r'missing.*field', r'required.*field', r'validation.*error',
            r'invalid.*data', r'parse.*error', r'json.*error', r'KeyError'
        ],
        'execution_error': [
            r'execution.*failed', r'agent.*failed', r'task.*failed',
            r'RuntimeError', r'Exception'
        ],
        'resource_error': [
            r'memory', r'disk.*space', r'out.*of.*memory', r'MemoryError',
            r'resource.*exhausted'
        ],
    }

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        # Compile regex patterns for efficiency
        self._compiled_normalization = [
            (re.compile(pattern, re.IGNORECASE), replacement)
            for pattern, replacement in self.NORMALIZATION_PATTERNS
        ]

    def generate_signature(
        self,
        error_message: str,
        error_code: str = None,
        provider: str = None,
        source_type: str = None,
        context: Dict[str, Any] = None
    ) -> Tuple[str, str, str]:
        """
        Generate a stable signature for a failure.

        Args:
            error_message: The error message
            error_code: HTTP status code or error code
            provider: Provider name (openai, anthropic, etc.)
            source_type: Source type (experiment, agent_execution, etc.)
            context: Additional context dict

        Returns:
            Tuple of (signature, category, description)
        """
        context = context or {}

        # Normalize the error message
        normalized_msg = self._normalize_error_message(error_message)

        # Detect provider if not provided
        if not provider:
            provider = self._detect_provider(error_message, context)

        # Detect error type from patterns
        error_type = self._detect_error_type(
            error_message, error_code, provider, normalized_msg
        )

        # Detect category
        category = self._detect_category(error_message, provider, error_type)

        # Build signature
        signature = self._build_signature(
            provider=provider,
            error_type=error_type,
            error_code=error_code,
            source_type=source_type,
            normalized_msg=normalized_msg,
            context=context
        )

        # Generate description
        description = self._generate_description(
            signature, provider, error_type, error_message
        )

        self.logger.debug(f"Generated signature: {signature} ({category})")

        return signature, category, description

    def _normalize_error_message(self, message: str) -> str:
        """
        Normalize error message by removing dynamic parts.

        Strips UUIDs, timestamps, IPs, etc. to create stable signatures.
        """
        if not message:
            return ""

        normalized = message

        # Apply all normalization patterns
        for pattern, replacement in self._compiled_normalization:
            normalized = pattern.sub(replacement, normalized)

        # Collapse multiple spaces
        normalized = re.sub(r'\s+', ' ', normalized)

        # Trim to reasonable length
        if len(normalized) > 200:
            normalized = normalized[:197] + '...'

        return normalized.strip()

    def _detect_provider(self, message: str, context: Dict[str, Any]) -> Optional[str]:
        """Detect provider from error message or context."""
        # Check context first
        if context.get('provider'):
            return context['provider'].lower()

        if context.get('model'):
            model = context['model'].lower()
            if 'gpt' in model or 'o1' in model or 'o3' in model:
                return 'openai'
            if 'claude' in model:
                return 'anthropic'
            if 'gemini' in model:
                return 'gemini'
            if 'deepseek' in model:
                return 'deepseek'
            if 'llama' in model or 'mistral' in model:
                return 'together'

        # Check message
        message_lower = message.lower()
        for provider in self.PROVIDER_PATTERNS:
            if provider in message_lower:
                return provider

        return None

    def _detect_error_type(
        self,
        message: str,
        error_code: str,
        provider: str,
        normalized_msg: str
    ) -> str:
        """Detect the specific error type."""
        message_lower = message.lower()

        # Check provider-specific patterns first
        if provider and provider in self.PROVIDER_PATTERNS:
            for error_type, patterns in self.PROVIDER_PATTERNS[provider].items():
                for pattern in patterns:
                    if re.search(pattern, message_lower):
                        return error_type
                    if error_code and re.search(pattern, str(error_code)):
                        return error_type

        # Generic detection
        if error_code:
            code_str = str(error_code)
            if code_str == '429':
                return 'rate_limit'
            if code_str == '401' or code_str == '403':
                return 'auth'
            if code_str.startswith('5'):
                return 'server'
            if code_str == '408':
                return 'timeout'

        # Pattern-based detection
        if re.search(r'timeout|timed.*out', message_lower):
            return 'timeout'
        if re.search(r'rate.*limit|quota', message_lower):
            return 'rate_limit'
        if re.search(r'auth|api.*key|unauthorized', message_lower):
            return 'auth'
        if re.search(r'connection|refused|network', message_lower):
            return 'connection'

        return 'unknown'

    def _detect_category(
        self,
        message: str,
        provider: str,
        error_type: str
    ) -> str:
        """Detect the failure category."""
        message_lower = message.lower()

        # Provider errors have highest priority
        if provider:
            return 'provider_error'

        # Check category patterns
        for category, patterns in self.CATEGORY_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    return category

        # Infer from error type
        if error_type == 'timeout':
            return 'timeout'

        return 'unknown'

    def _build_signature(
        self,
        provider: str,
        error_type: str,
        error_code: str,
        source_type: str,
        normalized_msg: str,
        context: Dict[str, Any]
    ) -> str:
        """Build the final signature string."""
        parts = []

        # Add provider or source type
        if provider:
            parts.append(provider.upper())
        elif source_type:
            parts.append(source_type.upper())

        # Add error code if available
        if error_code:
            parts.append(str(error_code))

        # Add error type
        if error_type and error_type != 'unknown':
            parts.append(error_type.upper())

        # If still empty, use hash of normalized message
        if not parts:
            msg_hash = hashlib.md5(normalized_msg.encode()).hexdigest()[:8]
            parts.append(f"ERROR_{msg_hash}")

        # Add agent name if it's an agent execution error
        if context.get('agent_name'):
            parts.append(context['agent_name'])

        # Add model if relevant
        if context.get('model') and provider:
            model = context['model'].replace('-', '_').upper()
            # Only add model if it adds information
            if model not in parts:
                parts.append(model[:20])  # Truncate long model names

        signature = '_'.join(parts)

        # Clean up signature
        signature = re.sub(r'[^A-Z0-9_]', '', signature.upper())
        signature = re.sub(r'_+', '_', signature)
        signature = signature.strip('_')

        return signature[:100]  # Cap length

    def _generate_description(
        self,
        signature: str,
        provider: str,
        error_type: str,
        original_message: str
    ) -> str:
        """Generate a human-readable description."""
        descriptions = {
            'rate_limit': f"{provider or 'API'} rate limit exceeded - too many requests",
            'auth': f"{provider or 'API'} authentication failed - invalid or expired credentials",
            'server': f"{provider or 'API'} server error - upstream service issue",
            'timeout': f"{provider or 'API'} request timeout - slow or unresponsive service",
            'connection': f"Connection error to {provider or 'service'} - network or service availability issue",
            'context_length': "Context length exceeded - input too long for model",
            'content_filter': "Content policy violation - input or output flagged",
        }

        if error_type in descriptions:
            return descriptions[error_type]

        # Fallback: truncated original message
        if original_message:
            return original_message[:200]

        return f"Failure with signature: {signature}"


# Singleton instance
_generator_instance: Optional[FailureSignatureGenerator] = None


def get_failure_signature_generator() -> FailureSignatureGenerator:
    """Get the singleton FailureSignatureGenerator instance."""
    global _generator_instance
    if _generator_instance is None:
        _generator_instance = FailureSignatureGenerator()
    return _generator_instance


def generate_failure_signature(
    error_message: str,
    error_code: str = None,
    provider: str = None,
    source_type: str = None,
    context: Dict[str, Any] = None
) -> Tuple[str, str, str]:
    """
    Convenience function to generate a failure signature.

    Returns:
        Tuple of (signature, category, description)
    """
    return get_failure_signature_generator().generate_signature(
        error_message=error_message,
        error_code=error_code,
        provider=provider,
        source_type=source_type,
        context=context
    )

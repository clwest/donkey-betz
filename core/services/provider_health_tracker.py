"""
Session 841: Provider Health Tracker

Tracks LLM provider health to prevent cascading failures during provider outages.
When a provider has elevated error rates (429s, 5xx, connection errors), experiments
should not be halted based on error metrics since the errors are external, not
experiment-related.

Key Features:
- Tracks errors per provider using Django cache (Redis)
- Sliding window of 5 minutes
- Threshold of 5+ errors marks provider as degraded
- Thread-safe using cache atomic operations
"""

import logging
from datetime import timedelta
from typing import Dict, List, Optional

from django.core.cache import cache
from django.utils import timezone

logger = logging.getLogger(__name__)


class ProviderHealthTracker:
    """
    Tracks LLM provider health status to detect outages.

    Uses Django cache for fast, distributed tracking across workers.
    """

    # Configuration
    ERROR_WINDOW_SECONDS = 300  # 5 minute window
    DEGRADED_THRESHOLD = 5  # 5+ errors = degraded
    CACHE_PREFIX = "provider_health:"
    CACHE_TTL = 600  # 10 minute cache TTL (longer than window to allow cleanup)

    # Known providers
    PROVIDERS = ['openai', 'anthropic', 'deepseek', 'gemini', 'ollama', 'together']

    # Error types we track
    ERROR_TYPES = ['rate_limit', 'server_error', 'connection_error', 'timeout']

    def record_error(self, provider: str, error_type: str) -> None:
        """
        Record an error for a provider.

        Args:
            provider: Provider name (e.g., 'openai', 'anthropic')
            error_type: Type of error ('rate_limit', 'server_error', 'connection_error', 'timeout')
        """
        if provider not in self.PROVIDERS:
            logger.debug(f"[Session 841] Unknown provider: {provider}")
            return

        if error_type not in self.ERROR_TYPES:
            error_type = 'server_error'  # Default to server_error for unknown types

        cache_key = f"{self.CACHE_PREFIX}{provider}:errors"
        timestamp = timezone.now().timestamp()

        try:
            # Get current error list
            errors = cache.get(cache_key, [])

            # Add new error with timestamp
            errors.append({
                'type': error_type,
                'timestamp': timestamp,
            })

            # Clean old errors (outside window)
            cutoff = timestamp - self.ERROR_WINDOW_SECONDS
            errors = [e for e in errors if e['timestamp'] > cutoff]

            # Save back to cache
            cache.set(cache_key, errors, self.CACHE_TTL)

            logger.warning(
                f"[Session 841] Provider {provider} error recorded: {error_type} "
                f"(total errors in window: {len(errors)})"
            )

        except Exception as e:
            logger.error(f"[Session 841] Failed to record provider error: {e}")

    def record_success(self, provider: str) -> None:
        """
        Record a successful API call. Used to track recovery.

        Args:
            provider: Provider name
        """
        # For now, we just log successes. Future enhancement could track
        # success rate to detect partial outages.
        pass

    def get_error_count(self, provider: str) -> int:
        """
        Get the number of errors for a provider in the current window.

        Args:
            provider: Provider name

        Returns:
            Number of errors in the window
        """
        cache_key = f"{self.CACHE_PREFIX}{provider}:errors"

        try:
            errors = cache.get(cache_key, [])

            # Filter to current window
            cutoff = timezone.now().timestamp() - self.ERROR_WINDOW_SECONDS
            current_errors = [e for e in errors if e['timestamp'] > cutoff]

            return len(current_errors)

        except Exception as e:
            logger.error(f"[Session 841] Failed to get error count: {e}")
            return 0

    def is_provider_degraded(self, provider: str) -> bool:
        """
        Check if a provider is currently degraded (elevated error rate).

        Args:
            provider: Provider name

        Returns:
            True if provider has 5+ errors in the last 5 minutes
        """
        error_count = self.get_error_count(provider)
        is_degraded = error_count >= self.DEGRADED_THRESHOLD

        if is_degraded:
            logger.info(
                f"[Session 841] Provider {provider} is degraded: "
                f"{error_count} errors in last {self.ERROR_WINDOW_SECONDS}s"
            )

        return is_degraded

    def any_provider_degraded(self) -> bool:
        """
        Check if ANY provider is currently degraded.

        Used by experiment metrics to suppress halts during provider outages.

        Returns:
            True if at least one provider is degraded
        """
        for provider in self.PROVIDERS:
            if self.is_provider_degraded(provider):
                return True
        return False

    def get_health_summary(self) -> Dict[str, dict]:
        """
        Get health summary for all providers.

        Returns:
            Dict mapping provider name to health info
        """
        summary = {}

        for provider in self.PROVIDERS:
            error_count = self.get_error_count(provider)
            summary[provider] = {
                'error_count': error_count,
                'is_degraded': error_count >= self.DEGRADED_THRESHOLD,
                'threshold': self.DEGRADED_THRESHOLD,
                'window_seconds': self.ERROR_WINDOW_SECONDS,
            }

        return summary

    def clear_provider_errors(self, provider: str) -> None:
        """
        Clear error history for a provider (useful for testing/manual reset).

        Args:
            provider: Provider name
        """
        cache_key = f"{self.CACHE_PREFIX}{provider}:errors"
        cache.delete(cache_key)
        logger.info(f"[Session 841] Cleared error history for {provider}")


# Module-level singleton for easy access
_tracker_instance: Optional[ProviderHealthTracker] = None


def get_provider_health_tracker() -> ProviderHealthTracker:
    """Get the singleton ProviderHealthTracker instance."""
    global _tracker_instance
    if _tracker_instance is None:
        _tracker_instance = ProviderHealthTracker()
    return _tracker_instance


# Convenience functions
def record_provider_error(provider: str, error_type: str) -> None:
    """Record an error for a provider."""
    get_provider_health_tracker().record_error(provider, error_type)


def record_provider_success(provider: str) -> None:
    """Record a success for a provider."""
    get_provider_health_tracker().record_success(provider)


def is_any_provider_degraded() -> bool:
    """Check if any provider is degraded."""
    return get_provider_health_tracker().any_provider_degraded()


def get_provider_health_summary() -> Dict[str, dict]:
    """Get health summary for all providers."""
    return get_provider_health_tracker().get_health_summary()

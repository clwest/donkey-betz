"""
Session 789: Centralized Redis connection helper.

This module provides a single point of truth for Redis connections,
ensuring all production code uses REDIS_URL from environment variables.

Usage:
    from core.utils.redis_helper import get_redis_client, get_redis_url

    # Get a Redis client
    r = get_redis_client()
    r = get_redis_client(db=2)  # Use specific database
    r = get_redis_client(decode_responses=True)

    # Get just the URL
    redis_url = get_redis_url()
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Default Redis URL - only used if REDIS_URL env var is not set
DEFAULT_REDIS_URL = 'redis://localhost:6379/0'


def get_redis_url(db: Optional[int] = None) -> str:
    """
    Get the Redis URL from environment or settings.

    Args:
        db: Optional database number to use (overrides default in URL)

    Returns:
        Redis URL string
    """
    # Try environment variable first
    redis_url = os.environ.get('REDIS_URL')

    if not redis_url:
        # Try Django settings
        try:
            from django.conf import settings
            redis_url = getattr(settings, 'REDIS_URL', None)
        except Exception as _e:
            logger.warning(
                "redis_helper.get_redis_url: swallowed (%s: %s) — degraded",
                type(_e).__name__, _e,
            )

    if not redis_url:
        redis_url = DEFAULT_REDIS_URL
        logger.debug(f"Using default Redis URL: {redis_url}")

    # If a specific db is requested, modify the URL
    if db is not None:
        # Parse the URL and replace the db number
        if '/' in redis_url.rstrip('/'):
            # URL has a path, replace the db number
            base_url = redis_url.rsplit('/', 1)[0]
            redis_url = f"{base_url}/{db}"
        else:
            # URL has no path, add the db number
            redis_url = f"{redis_url.rstrip('/')}/{db}"

    return redis_url


def get_redis_client(
    db: Optional[int] = None,
    decode_responses: bool = True,
    **kwargs
):
    """
    Get a Redis client using the proper environment configuration.

    Args:
        db: Optional database number (0-15)
        decode_responses: Whether to decode bytes to strings (default: True)
        **kwargs: Additional arguments passed to Redis client

    Returns:
        redis.Redis client instance
    """
    import redis

    redis_url = get_redis_url(db=db)

    return redis.Redis.from_url(
        redis_url,
        decode_responses=decode_responses,
        **kwargs
    )


def get_async_redis_client(
    db: Optional[int] = None,
    decode_responses: bool = True,
    **kwargs
):
    """
    Get an async Redis client using the proper environment configuration.

    Args:
        db: Optional database number (0-15)
        decode_responses: Whether to decode bytes to strings (default: True)
        **kwargs: Additional arguments passed to Redis client

    Returns:
        aioredis/redis.asyncio Redis client instance
    """
    try:
        import redis.asyncio as aioredis
    except ImportError:
        import aioredis

    redis_url = get_redis_url(db=db)

    return aioredis.from_url(
        redis_url,
        decode_responses=decode_responses,
        **kwargs
    )

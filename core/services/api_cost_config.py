"""
API Cost Configuration - Session 769
=====================================

Centralized configuration for external API costs.
Used by services to calculate and track costs for:
- ElevenLabs (TTS)
- Stability AI (Image Generation)
- Runway ML (Video Generation)
- Trained/Pre-recorded Voices

These rates should be updated periodically as API pricing changes.
"""

from decimal import Decimal
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# ElevenLabs TTS Pricing
# =============================================================================
# Source: https://elevenlabs.io/pricing/api
# Rates as of January 2026

ELEVENLABS_COSTS = {
    # Cost per 1,000 characters by plan
    'free': Decimal('0.00'),        # Free tier (limited)
    'starter': Decimal('0.30'),     # $0.30 per 1,000 chars overage
    'creator': Decimal('0.30'),     # $0.30 per 1,000 chars overage
    'pro': Decimal('0.24'),         # $0.24 per 1,000 chars overage
    'scale': Decimal('0.18'),       # $0.18 per 1,000 chars overage
    'business': Decimal('0.12'),    # $0.12 per 1,000 chars overage

    # Default rate to use (assume Pro plan)
    'default_per_1000_chars': Decimal('0.24'),

    # Model-specific multipliers (Turbo is 0.5x cost)
    'models': {
        'eleven_monolingual_v1': Decimal('1.0'),
        'eleven_multilingual_v1': Decimal('1.0'),
        'eleven_multilingual_v2': Decimal('1.0'),
        'eleven_turbo_v2': Decimal('0.5'),
        'eleven_turbo_v2_5': Decimal('0.5'),
    },
}


# =============================================================================
# Stability AI Image Generation Pricing
# =============================================================================
# Source: https://platform.stability.ai/pricing
# Rates as of January 2026

STABILITY_COSTS = {
    # Cost per credit
    'cost_per_credit': Decimal('0.01'),

    # Credits per image by model/resolution
    'models': {
        'stable-diffusion-xl-1024-v1-0': {
            '1024x1024': 6.5,
            '1152x896': 6.5,
            '896x1152': 6.5,
            '1216x832': 6.5,
            '832x1216': 6.5,
            'default': 6.5,
        },
        'stable-diffusion-v1-6': {
            '512x512': 1.0,
            '768x768': 2.0,
            'default': 1.5,
        },
        'stable-image-core': {
            'default': 3.0,
        },
        'stable-image-ultra': {
            'default': 8.0,
        },
        'sd3-large': {
            'default': 6.5,
        },
        'sd3-large-turbo': {
            'default': 4.0,
        },
        'sd3-medium': {
            'default': 3.5,
        },
    },

    # Default if model not specified
    'default_credits_per_image': Decimal('6.5'),
}


# =============================================================================
# Runway ML Video Generation Pricing
# =============================================================================
# Source: https://docs.dev.runwayml.com/guides/pricing/
# Rates as of January 2026

RUNWAY_COSTS = {
    # Cost per credit
    'cost_per_credit': Decimal('0.01'),

    # Credits per second by model
    'models': {
        'gen-4.5': {
            'credits_per_second': 25,
            'cost_per_second': Decimal('0.25'),
        },
        'gen-4': {
            'credits_per_second': 12,
            'cost_per_second': Decimal('0.12'),
        },
        'gen-4-turbo': {
            'credits_per_second': 5,
            'cost_per_second': Decimal('0.05'),
        },
        'gen-3-alpha': {
            'credits_per_second': 10,
            'cost_per_second': Decimal('0.10'),
        },
        'gen-3-alpha-turbo': {
            'credits_per_second': 8,
            'cost_per_second': Decimal('0.08'),
        },
    },

    # Resolution multipliers
    'resolution_multipliers': {
        '720p': Decimal('1.0'),
        '1080p': Decimal('1.2'),
        '4k': Decimal('1.5'),
    },

    # Frame rate multipliers
    'fps_multipliers': {
        24: Decimal('1.0'),
        30: Decimal('1.1'),
        60: Decimal('1.3'),
    },

    # Default model
    'default_model': 'gen-4-turbo',
    'default_cost_per_second': Decimal('0.05'),
}


# =============================================================================
# Trained/Pre-recorded Voice Costs
# =============================================================================
# Custom voices that have been trained or pre-recorded

TRAINED_VOICE_COSTS = {
    # Cost per use of a trained voice
    'cost_per_use': Decimal('0.05'),

    # Cost per minute for pre-recorded audio
    'prerecorded_per_minute': Decimal('0.10'),

    # Voice cloning training cost (one-time)
    'clone_training_cost': Decimal('5.00'),
}


# =============================================================================
# Spider/Data Costs (mostly negligible)
# =============================================================================

SPIDER_COSTS = {
    # Most spiders use free APIs, but some have costs
    'paid_apis': {
        'newsapi': Decimal('0.0001'),      # Per request
        'polygon_finance': Decimal('0.0001'),
        'finnhub': Decimal('0.0001'),
        'alpha_vantage': Decimal('0.0001'),
    },
    'default': Decimal('0.0000'),  # Free (RSS, scraping, etc.)
}


# =============================================================================
# Cost Calculation Helpers
# =============================================================================

def calculate_elevenlabs_cost(
    text: str,
    model: str = 'eleven_monolingual_v1',
    plan: str = 'pro'
) -> Dict[str, Any]:
    """
    Calculate ElevenLabs TTS cost for given text.

    Args:
        text: The text to convert to speech
        model: ElevenLabs model ID
        plan: Subscription plan (affects overage rate)

    Returns:
        Dict with character_count, cost, model, plan
    """
    char_count = len(text)

    # Get base rate
    base_rate = ELEVENLABS_COSTS.get(plan, ELEVENLABS_COSTS['default_per_1000_chars'])

    # Get model multiplier
    model_multiplier = ELEVENLABS_COSTS['models'].get(model, Decimal('1.0'))

    # Calculate cost: (chars / 1000) * rate * multiplier
    cost = (Decimal(char_count) / Decimal('1000')) * base_rate * model_multiplier

    return {
        'character_count': char_count,
        'cost': round(cost, 6),
        'model': model,
        'plan': plan,
        'rate_per_1000': float(base_rate),
    }


def calculate_stability_cost(
    model: str = 'stable-diffusion-xl-1024-v1-0',
    resolution: str = 'default',
    image_count: int = 1
) -> Dict[str, Any]:
    """
    Calculate Stability AI image generation cost.

    Args:
        model: Stability model ID
        resolution: Image resolution
        image_count: Number of images generated

    Returns:
        Dict with credits_used, cost, model, resolution, image_count
    """
    # Get model config
    model_config = STABILITY_COSTS['models'].get(
        model,
        {'default': float(STABILITY_COSTS['default_credits_per_image'])}
    )

    # Get credits for resolution
    credits_per_image = Decimal(str(model_config.get(resolution, model_config.get('default', 6.5))))

    # Calculate total
    total_credits = credits_per_image * image_count
    cost = total_credits * STABILITY_COSTS['cost_per_credit']

    return {
        'credits_used': float(total_credits),
        'cost': round(cost, 6),
        'model': model,
        'resolution': resolution,
        'image_count': image_count,
        'cost_per_credit': float(STABILITY_COSTS['cost_per_credit']),
    }


def calculate_runway_cost(
    duration_seconds: float,
    model: str = 'gen-4-turbo',
    resolution: str = '720p',
    fps: int = 24
) -> Dict[str, Any]:
    """
    Calculate Runway ML video generation cost.

    Args:
        duration_seconds: Video duration in seconds
        model: Runway model ID
        resolution: Video resolution
        fps: Frames per second

    Returns:
        Dict with credits_used, cost, model, duration, resolution, fps
    """
    # Get model config
    model_config = RUNWAY_COSTS['models'].get(model, {
        'cost_per_second': RUNWAY_COSTS['default_cost_per_second'],
        'credits_per_second': 5,
    })

    # Base cost
    base_cost = model_config['cost_per_second'] * Decimal(str(duration_seconds))

    # Apply multipliers
    res_multiplier = RUNWAY_COSTS['resolution_multipliers'].get(resolution, Decimal('1.0'))
    fps_multiplier = RUNWAY_COSTS['fps_multipliers'].get(fps, Decimal('1.0'))

    total_cost = base_cost * res_multiplier * fps_multiplier
    credits = model_config['credits_per_second'] * duration_seconds

    return {
        'credits_used': credits,
        'cost': round(total_cost, 6),
        'model': model,
        'duration_seconds': duration_seconds,
        'resolution': resolution,
        'fps': fps,
    }


def calculate_trained_voice_cost(
    duration_seconds: Optional[float] = None,
    is_clone: bool = False
) -> Dict[str, Any]:
    """
    Calculate cost for trained/pre-recorded voice usage.

    Args:
        duration_seconds: Duration of pre-recorded audio used
        is_clone: Whether this is a cloned voice

    Returns:
        Dict with cost breakdown
    """
    cost = TRAINED_VOICE_COSTS['cost_per_use']

    if duration_seconds:
        minutes = Decimal(str(duration_seconds)) / Decimal('60')
        cost += minutes * TRAINED_VOICE_COSTS['prerecorded_per_minute']

    return {
        'cost': round(cost, 6),
        'duration_seconds': duration_seconds,
        'is_clone': is_clone,
        'base_cost': float(TRAINED_VOICE_COSTS['cost_per_use']),
    }


# =============================================================================
# Aggregate Cost Summary
# =============================================================================

def aggregate_workflow_costs(
    llm_cost: Decimal = Decimal('0'),
    elevenlabs_cost: Decimal = Decimal('0'),
    stability_cost: Decimal = Decimal('0'),
    runway_cost: Decimal = Decimal('0'),
    trained_voice_cost: Decimal = Decimal('0'),
    spider_cost: Decimal = Decimal('0'),
) -> Dict[str, Any]:
    """
    Aggregate all costs for a workflow execution.

    Returns:
        Dict with breakdown and total
    """
    total = llm_cost + elevenlabs_cost + stability_cost + runway_cost + trained_voice_cost + spider_cost

    return {
        'breakdown': {
            'llm': float(llm_cost),
            'elevenlabs': float(elevenlabs_cost),
            'stability': float(stability_cost),
            'runway': float(runway_cost),
            'trained_voice': float(trained_voice_cost),
            'spider': float(spider_cost),
        },
        'total': float(total),
        'formatted': f'${float(total):.4f}',
    }

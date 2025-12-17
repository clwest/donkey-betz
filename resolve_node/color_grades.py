"""
Color Grade Presets for DaVinci Resolve
=======================================

Session 478: DaVinci Resolve Full Utilization

This module defines color grade presets that map to spider creative trends.
The system automatically selects the best grade based on:
1. Current spider trends (Dribbble, Behance, Pinterest)
2. Historical performance data (user ratings, usage patterns)
3. Learning loop recommendations

Each preset includes:
- DaVinci Resolve settings (color wheels, contrast, saturation)
- Spider style/color mappings for automatic matching
- Description for user understanding
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# COLOR GRADE PRESETS REGISTRY
# ============================================================================

COLOR_GRADE_PRESETS: Dict[str, Dict[str, Any]] = {

    # === CINEMATIC PRESETS ===

    "cinematic_warm": {
        "description": "Orange and teal cinematic look - Hollywood blockbuster style",
        "use_case": "Professional ads, dramatic scenes, commercial content",
        "spider_styles": ["cinematic", "film", "warm", "dramatic", "professional"],
        "spider_colors": ["warm", "terracotta", "earth-tones", "orange", "golden"],
        "resolve_settings": {
            "ColorWheels": {
                "lift": {"red": -0.10, "green": -0.05, "blue": 0.00},
                "gamma": {"red": 0.10, "green": 0.05, "blue": 0.00},
                "gain": {"red": 0.05, "green": 0.00, "blue": -0.05},
            },
            "Contrast": 1.10,
            "Saturation": 1.15,
            "Temperature": 200,  # Warmer
        },
    },

    "cinematic_cool": {
        "description": "Cool teal cinematic look - sci-fi and thriller style",
        "use_case": "Sci-fi content, thrillers, tech videos",
        "spider_styles": ["cinematic", "film", "cool", "futuristic", "thriller"],
        "spider_colors": ["cool", "teal", "blue", "steel", "silver"],
        "resolve_settings": {
            "ColorWheels": {
                "lift": {"red": 0.00, "green": 0.00, "blue": 0.10},
                "gamma": {"red": -0.05, "green": 0.00, "blue": 0.05},
                "gain": {"red": -0.05, "green": 0.00, "blue": 0.05},
            },
            "Contrast": 1.15,
            "Saturation": 0.95,
            "Temperature": -300,  # Cooler
        },
    },

    # === TRENDING STYLE PRESETS ===

    "cyberpunk_neon": {
        "description": "High contrast neon colors - futuristic and edgy",
        "use_case": "Tech content, gaming, music videos, futuristic brands",
        "spider_styles": ["cyberpunk", "neon", "futuristic", "tech", "gaming", "edgy"],
        "spider_colors": ["neon", "vibrant", "jewel-tones", "purple", "pink", "electric-blue"],
        "resolve_settings": {
            "ColorWheels": {
                "lift": {"red": 0.10, "green": -0.10, "blue": 0.20},
                "gamma": {"red": 0.00, "green": -0.10, "blue": 0.10},
                "gain": {"red": 0.10, "green": 0.00, "blue": 0.15},
            },
            "Contrast": 1.30,
            "Saturation": 1.40,
            "Temperature": -200,
            "Highlights": 10,  # Boost highlights
        },
    },

    "vintage_film": {
        "description": "Nostalgic film grain look - retro and authentic",
        "use_case": "Nostalgic content, indie films, vintage brands, lifestyle",
        "spider_styles": ["vintage", "retro", "film", "nostalgic", "analog", "indie"],
        "spider_colors": ["muted", "pastels", "dusty-rose", "sepia", "faded", "cream"],
        "resolve_settings": {
            "ColorWheels": {
                "lift": {"red": 0.05, "green": 0.02, "blue": 0.00},
                "gamma": {"red": 0.03, "green": 0.01, "blue": -0.02},
                "gain": {"red": 0.02, "green": 0.00, "blue": -0.03},
            },
            "Contrast": 0.95,
            "Saturation": 0.85,
            "FilmGrain": True,
            "FilmGrainStrength": 0.15,
        },
    },

    "nordic_cool": {
        "description": "Cool, desaturated Scandinavian look - clean and minimal",
        "use_case": "Scandinavian brands, minimalist content, clean aesthetics",
        "spider_styles": ["scandinavian", "minimalist", "clean", "nordic", "modern", "simple"],
        "spider_colors": ["cool", "neutrals", "sage", "grey", "white", "muted"],
        "resolve_settings": {
            "ColorWheels": {
                "lift": {"red": 0.00, "green": 0.02, "blue": 0.05},
                "gamma": {"red": -0.02, "green": 0.00, "blue": 0.02},
                "gain": {"red": -0.02, "green": 0.00, "blue": 0.03},
            },
            "Contrast": 1.05,
            "Saturation": 0.80,
            "Temperature": -500,
        },
    },

    # === LIFESTYLE PRESETS ===

    "sunset_golden": {
        "description": "Golden hour warmth - lifestyle and travel content",
        "use_case": "Lifestyle content, travel videos, outdoor scenes",
        "spider_styles": ["golden hour", "warm", "lifestyle", "travel", "outdoor", "sunny"],
        "spider_colors": ["warm", "golden", "yellow", "orange", "amber", "honey"],
        "resolve_settings": {
            "ColorWheels": {
                "lift": {"red": 0.05, "green": 0.02, "blue": -0.05},
                "gamma": {"red": 0.08, "green": 0.04, "blue": -0.02},
                "gain": {"red": 0.10, "green": 0.05, "blue": -0.05},
            },
            "Contrast": 1.05,
            "Saturation": 1.20,
            "Temperature": 400,
            "Highlights": -5,  # Recover highlights
        },
    },

    "moody_dark": {
        "description": "Dark and moody atmosphere - dramatic and mysterious",
        "use_case": "Dramatic content, noir style, mysterious brands, horror",
        "spider_styles": ["noir", "dramatic", "moody", "dark", "mysterious", "gothic"],
        "spider_colors": ["dark", "deep", "black", "charcoal", "shadow", "midnight"],
        "resolve_settings": {
            "ColorWheels": {
                "lift": {"red": -0.05, "green": -0.05, "blue": 0.00},
                "gamma": {"red": 0.00, "green": -0.02, "blue": 0.02},
                "gain": {"red": -0.05, "green": -0.05, "blue": 0.00},
            },
            "Contrast": 1.25,
            "Saturation": 0.90,
            "Shadows": -10,  # Crush blacks
        },
    },

    # === NATURAL PRESETS ===

    "natural_vibrant": {
        "description": "Enhanced natural colors - vibrant but realistic",
        "use_case": "Nature documentaries, product videos, real estate",
        "spider_styles": ["natural", "vibrant", "realistic", "organic", "fresh", "bright"],
        "spider_colors": ["natural", "green", "blue", "earth", "sky", "organic"],
        "resolve_settings": {
            "ColorWheels": {
                "lift": {"red": 0.00, "green": 0.02, "blue": 0.00},
                "gamma": {"red": 0.02, "green": 0.03, "blue": 0.01},
                "gain": {"red": 0.00, "green": 0.02, "blue": 0.02},
            },
            "Contrast": 1.08,
            "Saturation": 1.15,
            "Temperature": 0,
        },
    },

    "pastel_soft": {
        "description": "Soft pastel tones - gentle and feminine",
        "use_case": "Fashion, beauty, lifestyle brands, wedding videos",
        "spider_styles": ["pastel", "soft", "feminine", "gentle", "romantic", "dreamy"],
        "spider_colors": ["pastels", "blush", "lavender", "mint", "peach", "soft-pink"],
        "resolve_settings": {
            "ColorWheels": {
                "lift": {"red": 0.05, "green": 0.03, "blue": 0.05},
                "gamma": {"red": 0.03, "green": 0.02, "blue": 0.03},
                "gain": {"red": 0.02, "green": 0.00, "blue": 0.02},
            },
            "Contrast": 0.95,
            "Saturation": 0.90,
            "Temperature": 100,
            "Highlights": 5,
        },
    },

    # === BROADCAST PRESETS ===

    "broadcast_standard": {
        "description": "Broadcast-safe colors - professional TV standard",
        "use_case": "TV commercials, broadcast content, professional delivery",
        "spider_styles": ["professional", "broadcast", "corporate", "commercial", "standard"],
        "spider_colors": ["balanced", "neutral", "standard", "broadcast-safe"],
        "resolve_settings": {
            "ColorWheels": {
                "lift": {"red": 0.00, "green": 0.00, "blue": 0.00},
                "gamma": {"red": 0.00, "green": 0.00, "blue": 0.00},
                "gain": {"red": 0.00, "green": 0.00, "blue": 0.00},
            },
            "Contrast": 1.00,
            "Saturation": 1.00,
            "BroadcastSafe": True,
        },
    },

    "corporate_clean": {
        "description": "Clean corporate look - professional and trustworthy",
        "use_case": "Corporate videos, presentations, B2B content",
        "spider_styles": ["corporate", "clean", "professional", "business", "trustworthy"],
        "spider_colors": ["blue", "grey", "white", "navy", "professional"],
        "resolve_settings": {
            "ColorWheels": {
                "lift": {"red": -0.02, "green": 0.00, "blue": 0.02},
                "gamma": {"red": 0.00, "green": 0.00, "blue": 0.02},
                "gain": {"red": -0.02, "green": 0.00, "blue": 0.03},
            },
            "Contrast": 1.05,
            "Saturation": 0.95,
            "Temperature": -100,
        },
    },
}


# ============================================================================
# TREND MATCHING FUNCTIONS
# ============================================================================

def get_all_presets() -> List[str]:
    """Return list of all available preset names."""
    return list(COLOR_GRADE_PRESETS.keys())


def get_preset(preset_name: str) -> Optional[Dict[str, Any]]:
    """Get a specific preset by name."""
    return COLOR_GRADE_PRESETS.get(preset_name)


def match_grade_to_trends(spider_trends: Dict[str, Any]) -> str:
    """
    Match spider creative trends to the best color grade preset.

    Algorithm:
    1. Extract trending styles and colors from spider data
    2. Score each preset based on matches
    3. Return highest scoring preset

    Args:
        spider_trends: Dict with 'trending_styles' and 'trending_colors' keys
                      from SpiderIntelligenceService.get_creative_trends()

    Returns:
        Name of best matching preset (defaults to 'natural_vibrant')
    """
    if not spider_trends:
        return "natural_vibrant"

    # Extract trending data
    trending_styles = []
    trending_colors = []

    # Handle different formats from spider service
    if 'trending_styles' in spider_trends:
        for item in spider_trends['trending_styles']:
            if isinstance(item, dict):
                trending_styles.append(item.get('style', '').lower())
            elif isinstance(item, str):
                trending_styles.append(item.lower())

    if 'trending_colors' in spider_trends:
        for item in spider_trends['trending_colors']:
            if isinstance(item, dict):
                trending_colors.append(item.get('palette', '').lower())
            elif isinstance(item, str):
                trending_colors.append(item.lower())

    # Also check 'keywords' field
    if 'keywords' in spider_trends:
        for keyword in spider_trends.get('keywords', []):
            if isinstance(keyword, str):
                trending_styles.append(keyword.lower())

    logger.debug(f"Matching trends - styles: {trending_styles}, colors: {trending_colors}")

    # Score each preset
    preset_scores: Dict[str, float] = {}

    for preset_name, preset_config in COLOR_GRADE_PRESETS.items():
        score = 0.0

        # Match styles (weight: 2.0)
        for style in preset_config.get('spider_styles', []):
            if style.lower() in trending_styles:
                score += 2.0
            # Partial match
            elif any(style.lower() in ts or ts in style.lower() for ts in trending_styles):
                score += 1.0

        # Match colors (weight: 1.5)
        for color in preset_config.get('spider_colors', []):
            if color.lower() in trending_colors:
                score += 1.5
            # Partial match
            elif any(color.lower() in tc or tc in color.lower() for tc in trending_colors):
                score += 0.75

        preset_scores[preset_name] = score

    # Return best match (or default)
    if preset_scores:
        best_preset = max(preset_scores, key=preset_scores.get)
        best_score = preset_scores[best_preset]

        if best_score > 0:
            logger.info(f"Matched trends to preset '{best_preset}' (score: {best_score})")
            return best_preset

    # Default fallback
    logger.info("No strong trend match, defaulting to 'natural_vibrant'")
    return "natural_vibrant"


def get_preset_for_use_case(use_case: str) -> str:
    """
    Find best preset for a described use case.

    Args:
        use_case: Description like "tech commercial" or "wedding video"

    Returns:
        Best matching preset name
    """
    use_case_lower = use_case.lower()

    # Score each preset by use_case match
    best_match = "natural_vibrant"
    best_score = 0

    for preset_name, preset_config in COLOR_GRADE_PRESETS.items():
        preset_use_case = preset_config.get('use_case', '').lower()

        # Count word matches
        score = sum(1 for word in use_case_lower.split() if word in preset_use_case)

        if score > best_score:
            best_score = score
            best_match = preset_name

    return best_match


def describe_preset(preset_name: str) -> str:
    """Get human-readable description of a preset."""
    preset = COLOR_GRADE_PRESETS.get(preset_name)
    if not preset:
        return f"Unknown preset: {preset_name}"

    return f"{preset_name}: {preset['description']} | Best for: {preset['use_case']}"


def list_presets_for_trend(trend_keyword: str) -> List[str]:
    """
    List presets that match a specific trend keyword.

    Args:
        trend_keyword: e.g., "cyberpunk", "warm", "minimalist"

    Returns:
        List of matching preset names
    """
    trend_lower = trend_keyword.lower()
    matches = []

    for preset_name, preset_config in COLOR_GRADE_PRESETS.items():
        # Check styles
        if any(trend_lower in style.lower() for style in preset_config.get('spider_styles', [])):
            matches.append(preset_name)
            continue

        # Check colors
        if any(trend_lower in color.lower() for color in preset_config.get('spider_colors', [])):
            matches.append(preset_name)
            continue

        # Check description
        if trend_lower in preset_config.get('description', '').lower():
            matches.append(preset_name)

    return matches

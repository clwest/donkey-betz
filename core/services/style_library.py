"""
Style Library - Centralized Knowledge of Available Visual Styles
================================================================

Session 394: Created for Human-in-the-Loop Brand Direction

This module provides:
1. All 80+ available style presets organized by category
2. Style recommendations based on business type/industry
3. Color palette suggestions by mood/industry
4. Logo direction options

Used by:
- BrandStrategyAgent: To make informed style recommendations
- Brand Review UI: To show users available options
- Creative Pipeline: To apply user-selected styles
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class StyleOption:
    """A single style option with metadata."""
    name: str
    display_name: str
    category: str
    description: str
    best_for: List[str]  # Industries/use cases this works well for
    mood: str  # The emotional feel (friendly, professional, edgy, etc.)
    example_prompt_suffix: str  # What gets added to prompts


# =============================================================================
# STYLE CATEGORIES AND OPTIONS
# =============================================================================

STYLE_CATEGORIES = {
    "photography": {
        "display_name": "Photography Styles",
        "description": "Realistic, professional photo-based looks",
        "icon": "📷"
    },
    "animation": {
        "display_name": "Animation & Cartoon",
        "description": "Fun, approachable animated styles",
        "icon": "🎬"
    },
    "digital_art": {
        "display_name": "Digital Art",
        "description": "Modern digital illustration styles",
        "icon": "🎨"
    },
    "traditional_art": {
        "display_name": "Traditional Art",
        "description": "Classic fine art techniques",
        "icon": "🖼️"
    },
    "artistic_movements": {
        "display_name": "Artistic Movements",
        "description": "Historical art movement styles",
        "icon": "🏛️"
    },
    "genre": {
        "display_name": "Genre Styles",
        "description": "Thematic visual styles",
        "icon": "🌟"
    },
    "3d_rendering": {
        "display_name": "3D & Rendering",
        "description": "Three-dimensional rendered looks",
        "icon": "🧊"
    },
    "cultural": {
        "display_name": "Cultural Styles",
        "description": "Traditional cultural art styles",
        "icon": "🌍"
    },
    "special": {
        "display_name": "Special & Unique",
        "description": "Distinctive special effect styles",
        "icon": "✨"
    }
}


# All 80+ styles organized by category
STYLE_LIBRARY: Dict[str, List[StyleOption]] = {
    "photography": [
        StyleOption("photorealistic", "Photorealistic", "photography",
                   "Ultra-realistic photography quality",
                   ["professional services", "real estate", "corporate", "products"],
                   "professional", "photorealistic, ultra detailed, professional photography, 8k uhd"),
        StyleOption("portrait", "Portrait Photography", "photography",
                   "Professional headshot/portrait style",
                   ["personal branding", "coaching", "consulting", "speakers"],
                   "trustworthy", "portrait photography, 85mm lens, f/1.8, studio lighting"),
        StyleOption("fashion", "Fashion Photography", "photography",
                   "High-fashion editorial style",
                   ["fashion", "beauty", "lifestyle", "luxury brands"],
                   "aspirational", "fashion photography, vogue style, editorial, studio lighting"),
        StyleOption("architectural", "Architectural", "photography",
                   "Clean modern architecture photography",
                   ["real estate", "architecture", "interior design", "construction"],
                   "sophisticated", "architectural photography, clean lines, modern"),
        StyleOption("vintage", "Vintage Photography", "photography",
                   "Retro nostalgic film look",
                   ["heritage brands", "artisan", "vintage shops", "classic products"],
                   "nostalgic", "vintage photography, retro, old film camera, sepia tones"),
    ],

    "animation": [
        StyleOption("pixar", "Pixar 3D", "animation",
                   "Friendly, approachable 3D animation like Pixar films",
                   ["children's products", "education", "family brands", "apps", "games"],
                   "friendly", "Pixar 3D animation style, Disney Pixar movie quality"),
        StyleOption("disney", "Disney Classic", "animation",
                   "Classic hand-drawn Disney animation style",
                   ["entertainment", "children", "family", "storytelling"],
                   "magical", "Disney animation style, classic cartoon, hand-drawn"),
        StyleOption("dreamworks", "DreamWorks 3D", "animation",
                   "Bold, expressive 3D animation style",
                   ["entertainment", "games", "apps", "youth brands"],
                   "energetic", "DreamWorks 3D animation style, stylized expressive characters"),
        StyleOption("ghibli", "Studio Ghibli", "animation",
                   "Whimsical hand-drawn with watercolor backgrounds",
                   ["wellness", "nature", "organic", "mindfulness", "creative"],
                   "serene", "Studio Ghibli anime style, watercolor backgrounds, soft colors"),
        StyleOption("anime", "Anime", "animation",
                   "Japanese animation style",
                   ["gaming", "entertainment", "youth culture", "tech"],
                   "dynamic", "anime style, manga art, cel shaded"),
        StyleOption("cartoon", "Modern Cartoon", "animation",
                   "Simple, colorful animated style",
                   ["apps", "startups", "education", "social media"],
                   "playful", "cartoon style, simple, colorful, animated series quality"),
        StyleOption("chibi", "Chibi/Kawaii", "animation",
                   "Cute super-deformed style",
                   ["gaming", "merchandise", "social apps", "youth brands"],
                   "cute", "chibi style, super deformed, cute, kawaii"),
    ],

    "digital_art": [
        StyleOption("digital_art", "Digital Art", "digital_art",
                   "Modern digital illustration trending on Artstation",
                   ["tech", "startups", "creative agencies", "gaming"],
                   "modern", "digital art, trending on artstation, concept art"),
        StyleOption("concept_art", "Concept Art", "digital_art",
                   "Professional game/movie concept art style",
                   ["gaming", "entertainment", "creative studios"],
                   "cinematic", "concept art, professional, game art, cinematic"),
        StyleOption("vector", "Vector Art", "digital_art",
                   "Clean, scalable vector illustration",
                   ["tech startups", "apps", "SaaS", "modern brands"],
                   "clean", "vector art, clean lines, flat design, minimalist"),
        StyleOption("isometric", "Isometric", "digital_art",
                   "3D isometric illustration style",
                   ["tech", "SaaS", "data visualization", "apps"],
                   "technical", "isometric art, 3d illustration, technical drawing"),
        StyleOption("low_poly", "Low Poly", "digital_art",
                   "Geometric low-polygon 3D style",
                   ["gaming", "tech", "modern startups", "apps"],
                   "geometric", "low poly art, geometric, faceted, polygon art"),
    ],

    "traditional_art": [
        StyleOption("watercolor", "Watercolor", "traditional_art",
                   "Soft, artistic watercolor painting",
                   ["wellness", "organic", "artisan", "boutique", "creative"],
                   "artistic", "watercolor painting, soft colors, artistic"),
        StyleOption("oil_painting", "Oil Painting", "traditional_art",
                   "Classical museum-quality oil painting",
                   ["luxury", "heritage", "fine dining", "art galleries"],
                   "prestigious", "oil painting on canvas, masterpiece, classical art"),
        StyleOption("ink", "Ink Drawing", "traditional_art",
                   "Detailed pen and ink illustration",
                   ["publishing", "editorial", "craft", "artisan"],
                   "sophisticated", "ink drawing, pen and ink, detailed linework"),
        StyleOption("pencil", "Pencil Sketch", "traditional_art",
                   "Hand-drawn pencil sketch style",
                   ["architecture", "design studios", "craft", "personal brands"],
                   "personal", "pencil drawing, detailed sketch, graphite"),
    ],

    "artistic_movements": [
        StyleOption("minimalist", "Minimalist", "artistic_movements",
                   "Clean, simple, lots of negative space",
                   ["tech", "luxury", "modern brands", "SaaS", "professional services"],
                   "sophisticated", "minimalist style, simple composition, clean lines, negative space"),
        StyleOption("art_deco", "Art Deco", "artistic_movements",
                   "1920s luxury geometric patterns",
                   ["luxury", "hospitality", "fashion", "premium brands"],
                   "luxurious", "art deco style, 1920s aesthetic, geometric patterns, luxury"),
        StyleOption("art_nouveau", "Art Nouveau", "artistic_movements",
                   "Flowing organic decorative style",
                   ["beauty", "wellness", "boutique", "artisan"],
                   "elegant", "art nouveau style, decorative, flowing lines, ornamental"),
        StyleOption("pop_art", "Pop Art", "artistic_movements",
                   "Bold, colorful Andy Warhol style",
                   ["entertainment", "media", "youth brands", "creative agencies"],
                   "bold", "pop art style, bold colors, halftone dots"),
        StyleOption("impressionist", "Impressionist", "artistic_movements",
                   "Soft, dreamy impressionist painting",
                   ["hospitality", "travel", "wine", "fine dining"],
                   "dreamy", "impressionist painting, monet style, loose brushwork"),
        StyleOption("surreal", "Surrealist", "artistic_movements",
                   "Dreamlike, unexpected surrealist imagery",
                   ["creative agencies", "art", "music", "entertainment"],
                   "creative", "surrealism, dreamlike, impossible geometry"),
    ],

    "genre": [
        StyleOption("cyberpunk", "Cyberpunk", "genre",
                   "Neon-lit futuristic high-tech style",
                   ["gaming", "tech (edgy)", "nightlife", "music"],
                   "edgy", "cyberpunk style, neon lights, futuristic, blade runner"),
        StyleOption("steampunk", "Steampunk", "genre",
                   "Victorian-era brass and clockwork aesthetic",
                   ["craft", "makers", "vintage tech", "artisan"],
                   "inventive", "steampunk style, victorian era, brass and copper, gears"),
        StyleOption("fantasy", "Fantasy", "genre",
                   "Magical, epic fantasy art style",
                   ["gaming", "entertainment", "publishing", "creative"],
                   "magical", "fantasy art, magical, ethereal, epic composition"),
        StyleOption("scifi", "Sci-Fi", "genre",
                   "Clean futuristic science fiction style",
                   ["tech", "space", "innovation", "research"],
                   "futuristic", "science fiction art, futuristic, space art, technological"),
        StyleOption("retro", "Retro 80s", "genre",
                   "Synthwave 80s neon nostalgia",
                   ["entertainment", "gaming", "music", "nightlife"],
                   "nostalgic", "retro style, 80s aesthetic, synthwave, neon colors"),
        StyleOption("gothic", "Gothic", "genre",
                   "Dark, atmospheric gothic style",
                   ["alternative fashion", "music", "art", "horror"],
                   "mysterious", "gothic art style, dark atmosphere, medieval"),
    ],

    "3d_rendering": [
        StyleOption("3d_render", "3D Render", "3d_rendering",
                   "High-quality 3D rendered imagery",
                   ["products", "tech", "architecture", "visualization"],
                   "polished", "3D render, octane render, unreal engine 5, ray tracing"),
        StyleOption("clay_render", "Clay Render", "3d_rendering",
                   "Soft 3D sculpture style",
                   ["products", "apps", "playful brands"],
                   "tactile", "clay render, 3d sculpture, soft lighting"),
    ],

    "cultural": [
        StyleOption("japanese", "Japanese Traditional", "cultural",
                   "Ukiyo-e woodblock print style",
                   ["tea", "wellness", "martial arts", "japanese culture"],
                   "zen", "traditional japanese art, ukiyo-e style, woodblock print"),
        StyleOption("chinese", "Chinese Traditional", "cultural",
                   "Ink wash mountain/water painting",
                   ["tea", "wellness", "asian cuisine", "traditional medicine"],
                   "harmonious", "traditional chinese painting, ink wash, mountain water"),
    ],

    "special": [
        StyleOption("neon", "Neon Glow", "special",
                   "Glowing neon light effects",
                   ["nightlife", "entertainment", "gaming", "events"],
                   "vibrant", "neon lights, glowing effects, dark background, vibrant colors"),
        StyleOption("pixel_art", "Pixel Art", "special",
                   "Retro 16-bit game style",
                   ["gaming", "indie games", "retro brands", "nostalgia"],
                   "retro", "pixel art, 16-bit style, retro gaming aesthetic"),
        StyleOption("graffiti", "Graffiti/Street Art", "special",
                   "Urban street art style",
                   ["urban fashion", "music", "youth culture", "streetwear"],
                   "urban", "graffiti art, street art, spray paint, urban"),
        StyleOption("holographic", "Holographic", "special",
                   "Iridescent rainbow holographic effect",
                   ["tech", "beauty", "futuristic brands", "premium"],
                   "futuristic", "holographic effect, iridescent, rainbow reflections"),
        StyleOption("glitch", "Glitch Art", "special",
                   "Digital distortion art style",
                   ["tech (edgy)", "music", "digital art", "experimental"],
                   "experimental", "glitch art, digital distortion, corrupted data"),
    ]
}


# =============================================================================
# COLOR PALETTE SUGGESTIONS
# =============================================================================

COLOR_PALETTES = {
    "professional": {
        "name": "Professional & Corporate",
        "colors": ["#1e3a5f", "#3d5a80", "#98c1d9", "#e0e1dd", "#293241"],
        "description": "Trust-inspiring blues and neutrals",
        "best_for": ["corporate", "finance", "legal", "consulting", "B2B"]
    },
    "friendly": {
        "name": "Friendly & Approachable",
        "colors": ["#ff6b6b", "#feca57", "#48dbfb", "#1dd1a1", "#5f27cd"],
        "description": "Warm, inviting colors that feel welcoming",
        "best_for": ["consumer apps", "education", "family brands", "social"]
    },
    "luxury": {
        "name": "Luxury & Premium",
        "colors": ["#1a1a2e", "#16213e", "#c9a959", "#e8d5b7", "#0f0e17"],
        "description": "Deep tones with gold accents",
        "best_for": ["luxury goods", "fashion", "jewelry", "hospitality"]
    },
    "tech_modern": {
        "name": "Modern Tech",
        "colors": ["#6366f1", "#8b5cf6", "#a855f7", "#06b6d4", "#0ea5e9"],
        "description": "Vibrant gradients popular in SaaS",
        "best_for": ["SaaS", "AI", "startups", "fintech"]
    },
    "nature_organic": {
        "name": "Nature & Organic",
        "colors": ["#2d6a4f", "#40916c", "#52b788", "#95d5b2", "#d8f3dc"],
        "description": "Earthy greens for natural brands",
        "best_for": ["organic", "wellness", "sustainability", "health"]
    },
    "bold_creative": {
        "name": "Bold & Creative",
        "colors": ["#f72585", "#7209b7", "#3a0ca3", "#4361ee", "#4cc9f0"],
        "description": "Electric gradients for creative brands",
        "best_for": ["creative agencies", "entertainment", "media", "art"]
    },
    "warm_earthy": {
        "name": "Warm & Earthy",
        "colors": ["#bc6c25", "#dda15e", "#fefae0", "#606c38", "#283618"],
        "description": "Warm terracotta and sage tones",
        "best_for": ["food", "home goods", "artisan", "craft"]
    },
    "minimal_mono": {
        "name": "Minimal Monochrome",
        "colors": ["#000000", "#333333", "#666666", "#999999", "#ffffff"],
        "description": "Sophisticated black and white",
        "best_for": ["luxury", "fashion", "architecture", "photography"]
    },
    "pastel_soft": {
        "name": "Soft Pastels",
        "colors": ["#ffd6e0", "#c1fba4", "#a0d2db", "#d4a5ff", "#ffb4a2"],
        "description": "Gentle, calming pastel tones",
        "best_for": ["baby products", "wellness", "beauty", "lifestyle"]
    },
    "cyberpunk_neon": {
        "name": "Cyberpunk Neon",
        "colors": ["#0d0221", "#0a0a23", "#ff00ff", "#00ffff", "#ff3366"],
        "description": "Dark with electric neon accents",
        "best_for": ["gaming", "nightlife", "music", "tech (edgy)"]
    }
}


# =============================================================================
# LOGO DIRECTION OPTIONS
# =============================================================================

LOGO_DIRECTIONS = {
    "icon_wordmark": {
        "name": "Icon + Wordmark",
        "description": "A symbol/icon paired with the brand name",
        "best_for": ["Most brands", "versatile usage", "brand recognition"],
        "examples": ["Apple", "Nike", "Spotify"]
    },
    "wordmark_only": {
        "name": "Wordmark Only",
        "description": "Stylized text-only logo",
        "best_for": ["Unique names", "luxury brands", "fashion"],
        "examples": ["Google", "Coca-Cola", "FedEx"]
    },
    "icon_only": {
        "name": "Icon/Symbol Only",
        "description": "Standalone symbol without text",
        "best_for": ["Established brands", "apps", "social media"],
        "examples": ["Apple", "Twitter/X", "Target"]
    },
    "lettermark": {
        "name": "Lettermark (Initials)",
        "description": "Logo using initials or abbreviation",
        "best_for": ["Long company names", "professional services"],
        "examples": ["IBM", "HBO", "NASA"]
    },
    "emblem": {
        "name": "Emblem/Badge",
        "description": "Icon contained within a badge or seal",
        "best_for": ["Heritage brands", "education", "government", "craft"],
        "examples": ["Starbucks", "Harvard", "NFL"]
    },
    "mascot": {
        "name": "Mascot Logo",
        "description": "Character-based logo",
        "best_for": ["Sports", "children's brands", "food", "gaming"],
        "examples": ["KFC", "Mailchimp", "Michelin"]
    }
}


# =============================================================================
# INDUSTRY-BASED RECOMMENDATIONS
# =============================================================================

INDUSTRY_RECOMMENDATIONS = {
    "tech_startup": {
        "recommended_styles": ["minimalist", "vector", "isometric", "digital_art"],
        "recommended_palettes": ["tech_modern", "bold_creative"],
        "recommended_logos": ["icon_wordmark", "wordmark_only"],
        "avoid_styles": ["gothic", "steampunk", "oil_painting"],
        "notes": "Modern, clean, scalable. Avoid overly trendy (cyberpunk) unless that's the brand identity."
    },
    "ai_tech": {
        "recommended_styles": ["minimalist", "vector", "3d_render", "digital_art"],
        "recommended_palettes": ["tech_modern", "professional", "bold_creative"],
        "recommended_logos": ["icon_wordmark", "lettermark"],
        "avoid_styles": ["cyberpunk", "neon"],  # Avoid cliches!
        "notes": "AI brands often default to cyberpunk - consider standing out with cleaner, more approachable styles."
    },
    "saas": {
        "recommended_styles": ["vector", "isometric", "minimalist", "cartoon"],
        "recommended_palettes": ["tech_modern", "friendly", "bold_creative"],
        "recommended_logos": ["icon_wordmark", "wordmark_only"],
        "avoid_styles": ["realistic", "gothic", "grunge"],
        "notes": "Friendly and approachable. Gradients are popular but use thoughtfully."
    },
    "ecommerce": {
        "recommended_styles": ["photorealistic", "minimalist", "vector"],
        "recommended_palettes": ["friendly", "warm_earthy", "bold_creative"],
        "recommended_logos": ["icon_wordmark", "wordmark_only"],
        "notes": "Depends heavily on what's being sold. Photography-forward for products."
    },
    "healthcare": {
        "recommended_styles": ["minimalist", "vector", "watercolor"],
        "recommended_palettes": ["professional", "nature_organic", "pastel_soft"],
        "recommended_logos": ["icon_wordmark", "emblem"],
        "avoid_styles": ["cyberpunk", "gothic", "graffiti"],
        "notes": "Trust and calm are key. Blues and greens dominate."
    },
    "food_restaurant": {
        "recommended_styles": ["photorealistic", "watercolor", "cartoon", "vintage"],
        "recommended_palettes": ["warm_earthy", "friendly", "nature_organic"],
        "recommended_logos": ["emblem", "icon_wordmark", "mascot"],
        "notes": "Appetite appeal is crucial. Warm colors work well."
    },
    "fitness_wellness": {
        "recommended_styles": ["photorealistic", "minimalist", "ghibli", "watercolor"],
        "recommended_palettes": ["nature_organic", "bold_creative", "pastel_soft"],
        "recommended_logos": ["icon_wordmark", "icon_only"],
        "notes": "Energy or calm depending on focus. Nature imagery works well."
    },
    "education": {
        "recommended_styles": ["pixar", "cartoon", "vector", "isometric"],
        "recommended_palettes": ["friendly", "professional", "bold_creative"],
        "recommended_logos": ["emblem", "icon_wordmark", "mascot"],
        "notes": "Approachable and trustworthy. Age-appropriate styling."
    },
    "luxury_fashion": {
        "recommended_styles": ["minimalist", "fashion", "art_deco", "oil_painting"],
        "recommended_palettes": ["luxury", "minimal_mono"],
        "recommended_logos": ["wordmark_only", "icon_wordmark"],
        "avoid_styles": ["cartoon", "pixel_art", "chibi"],
        "notes": "Sophistication and exclusivity. Less is more."
    },
    "gaming": {
        "recommended_styles": ["concept_art", "anime", "pixel_art", "cyberpunk", "fantasy"],
        "recommended_palettes": ["bold_creative", "cyberpunk_neon"],
        "recommended_logos": ["icon_wordmark", "mascot", "emblem"],
        "notes": "Genre-dependent. Can be more expressive than other industries."
    },
    "creative_agency": {
        "recommended_styles": ["pop_art", "surreal", "digital_art", "graffiti"],
        "recommended_palettes": ["bold_creative", "minimal_mono"],
        "recommended_logos": ["wordmark_only", "icon_wordmark"],
        "notes": "Showcase creativity but stay professional."
    },
    "podcast_media": {
        "recommended_styles": ["cartoon", "vector", "pop_art", "digital_art"],
        "recommended_palettes": ["bold_creative", "friendly", "tech_modern"],
        "recommended_logos": ["icon_wordmark", "icon_only"],
        "notes": "Needs to work well as small square artwork. Bold and recognizable."
    },
    "finance": {
        "recommended_styles": ["minimalist", "vector", "architectural"],
        "recommended_palettes": ["professional", "luxury", "minimal_mono"],
        "recommended_logos": ["wordmark_only", "lettermark", "icon_wordmark"],
        "avoid_styles": ["cartoon", "graffiti", "psychedelic"],
        "notes": "Trust and stability are paramount. Conservative but modern."
    }
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_all_styles() -> List[StyleOption]:
    """Get all available styles as a flat list."""
    all_styles = []
    for category_styles in STYLE_LIBRARY.values():
        all_styles.extend(category_styles)
    return all_styles


def get_styles_by_category(category: str) -> List[StyleOption]:
    """Get styles for a specific category."""
    return STYLE_LIBRARY.get(category, [])


def get_style_by_name(name: str) -> Optional[StyleOption]:
    """Find a style by its name."""
    for category_styles in STYLE_LIBRARY.values():
        for style in category_styles:
            if style.name == name:
                return style
    return None


def get_recommended_styles_for_industry(industry: str) -> Dict[str, Any]:
    """Get style recommendations for a specific industry."""
    # Try exact match first
    if industry.lower() in INDUSTRY_RECOMMENDATIONS:
        return INDUSTRY_RECOMMENDATIONS[industry.lower()]

    # Try partial match
    for key, rec in INDUSTRY_RECOMMENDATIONS.items():
        if key in industry.lower() or industry.lower() in key:
            return rec

    # Default recommendations
    return {
        "recommended_styles": ["minimalist", "vector", "digital_art"],
        "recommended_palettes": ["professional", "tech_modern"],
        "recommended_logos": ["icon_wordmark"],
        "notes": "Default recommendations - consider your specific audience and positioning."
    }


def detect_industry_from_idea(business_idea: str) -> str:
    """Attempt to detect industry from a business idea description."""
    idea_lower = business_idea.lower()

    # Check for keywords
    if any(word in idea_lower for word in ['ai', 'machine learning', 'artificial intelligence', 'ml', 'neural']):
        return 'ai_tech'
    if any(word in idea_lower for word in ['saas', 'software', 'platform', 'app', 'tool']):
        return 'saas'
    if any(word in idea_lower for word in ['podcast', 'media', 'content', 'streaming', 'video']):
        return 'podcast_media'
    if any(word in idea_lower for word in ['game', 'gaming', 'esport']):
        return 'gaming'
    if any(word in idea_lower for word in ['health', 'medical', 'wellness', 'therapy', 'clinic']):
        return 'healthcare'
    if any(word in idea_lower for word in ['food', 'restaurant', 'cafe', 'cuisine', 'meal']):
        return 'food_restaurant'
    if any(word in idea_lower for word in ['fitness', 'gym', 'workout', 'yoga', 'training']):
        return 'fitness_wellness'
    if any(word in idea_lower for word in ['education', 'learning', 'course', 'school', 'teach']):
        return 'education'
    if any(word in idea_lower for word in ['luxury', 'fashion', 'boutique', 'designer']):
        return 'luxury_fashion'
    if any(word in idea_lower for word in ['finance', 'bank', 'investment', 'fintech', 'trading']):
        return 'finance'
    if any(word in idea_lower for word in ['creative', 'design', 'agency', 'studio']):
        return 'creative_agency'
    if any(word in idea_lower for word in ['shop', 'store', 'ecommerce', 'marketplace', 'retail']):
        return 'ecommerce'
    if any(word in idea_lower for word in ['startup', 'tech']):
        return 'tech_startup'

    return 'tech_startup'  # Default


def get_brand_recommendations(business_idea: str) -> Dict[str, Any]:
    """
    Get comprehensive brand recommendations for a business idea.

    Returns:
        Dict with style_options, color_palettes, logo_directions, and industry_notes
    """
    industry = detect_industry_from_idea(business_idea)
    industry_rec = get_recommended_styles_for_industry(industry)

    # Get full style objects for recommended styles
    recommended_style_objects = []
    for style_name in industry_rec.get('recommended_styles', []):
        style = get_style_by_name(style_name)
        if style:
            recommended_style_objects.append({
                'name': style.name,
                'display_name': style.display_name,
                'category': style.category,
                'description': style.description,
                'mood': style.mood
            })

    # Get recommended palettes
    recommended_palette_objects = []
    for palette_name in industry_rec.get('recommended_palettes', []):
        if palette_name in COLOR_PALETTES:
            palette = COLOR_PALETTES[palette_name]
            recommended_palette_objects.append({
                'id': palette_name,
                'name': palette['name'],
                'colors': palette['colors'],
                'description': palette['description']
            })

    # Get recommended logo directions
    recommended_logo_objects = []
    for logo_type in industry_rec.get('recommended_logos', []):
        if logo_type in LOGO_DIRECTIONS:
            logo = LOGO_DIRECTIONS[logo_type]
            recommended_logo_objects.append({
                'id': logo_type,
                'name': logo['name'],
                'description': logo['description'],
                'examples': logo['examples']
            })

    # Get styles to avoid
    avoid_styles = industry_rec.get('avoid_styles', [])

    return {
        'detected_industry': industry,
        'style_options': recommended_style_objects,
        'avoid_styles': avoid_styles,
        'color_palettes': recommended_palette_objects,
        'logo_directions': recommended_logo_objects,
        'industry_notes': industry_rec.get('notes', ''),
        'all_categories': list(STYLE_CATEGORIES.keys()),
        'total_styles_available': len(get_all_styles())
    }


def get_style_library_summary() -> str:
    """
    Get a text summary of available styles for injection into GPT prompts.
    """
    summary = "AVAILABLE VISUAL STYLES (80+ options across 9 categories):\n\n"

    for category_id, category_info in STYLE_CATEGORIES.items():
        styles = STYLE_LIBRARY.get(category_id, [])
        if styles:
            summary += f"{category_info['icon']} {category_info['display_name']}:\n"
            for style in styles[:5]:  # Show first 5 per category
                summary += f"  - {style.display_name}: {style.description} (mood: {style.mood})\n"
            if len(styles) > 5:
                summary += f"  ... and {len(styles) - 5} more\n"
            summary += "\n"

    summary += "\nIMPORTANT: Avoid defaulting to 'cyberpunk' for tech/AI brands - consider minimalist, vector, or other modern styles that differentiate the brand.\n"

    return summary

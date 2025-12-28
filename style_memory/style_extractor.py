"""
Style Extractor - Extract real style elements from prompts and images using GPT.

Session 179: Fixes the hardcoded style elements bug in capture_interaction().
Instead of always storing ['minimalist', 'bold', 'contemporary'], this module
extracts actual style characteristics from the prompt text.
"""

import logging
import json
import re
from typing import List, Dict, Any, Optional
from django.conf import settings

logger = logging.getLogger(__name__)

# Common style keywords for fast extraction (no API call needed)
STYLE_KEYWORDS = {
    # Art styles
    'minimalist': 'minimalist',
    'minimal': 'minimalist',
    'bold': 'bold',
    'vibrant': 'vibrant',
    'muted': 'muted',
    'pastel': 'pastel',
    'neon': 'neon',
    'vintage': 'vintage',
    'retro': 'retro',
    'modern': 'modern',
    'contemporary': 'contemporary',
    'classical': 'classical',
    'abstract': 'abstract',
    'realistic': 'realistic',
    'photorealistic': 'photorealistic',
    'surreal': 'surreal',
    'surrealist': 'surreal',
    'impressionist': 'impressionist',
    'expressionist': 'expressionist',
    'pop art': 'pop art',
    'art deco': 'art deco',
    'art nouveau': 'art nouveau',
    'cyberpunk': 'cyberpunk',
    'steampunk': 'steampunk',
    'fantasy': 'fantasy',
    'sci-fi': 'sci-fi',
    'anime': 'anime',
    'manga': 'manga',
    'cartoon': 'cartoon',
    'comic': 'comic book',
    'watercolor': 'watercolor',
    'oil painting': 'oil painting',
    'digital art': 'digital art',
    'pixel art': 'pixel art',
    '3d render': '3d render',
    'cinematic': 'cinematic',
    'dramatic': 'dramatic',
    'moody': 'moody',
    'dark': 'dark',
    'light': 'light',
    'bright': 'bright',
    'soft': 'soft',
    'sharp': 'sharp',
    'detailed': 'detailed',
    'simple': 'simple',
    'complex': 'complex',
    'elegant': 'elegant',
    'rustic': 'rustic',
    'futuristic': 'futuristic',
    'gothic': 'gothic',
    'baroque': 'baroque',
    'minimalistic': 'minimalist',
    'ornate': 'ornate',
    'geometric': 'geometric',
    'organic': 'organic',
    'natural': 'natural',
    'artificial': 'artificial',
    'handmade': 'handmade',
    'professional': 'professional',
    'amateur': 'amateur',
    'studio': 'studio',
    'outdoor': 'outdoor',
    'indoor': 'indoor',
}

# Color keywords
COLOR_KEYWORDS = {
    'red': '#FF0000',
    'blue': '#0000FF',
    'green': '#00FF00',
    'yellow': '#FFFF00',
    'orange': '#FFA500',
    'purple': '#800080',
    'pink': '#FFC0CB',
    'brown': '#8B4513',
    'black': '#000000',
    'white': '#FFFFFF',
    'gray': '#808080',
    'grey': '#808080',
    'gold': '#FFD700',
    'silver': '#C0C0C0',
    'bronze': '#CD7F32',
    'teal': '#008080',
    'cyan': '#00FFFF',
    'magenta': '#FF00FF',
    'turquoise': '#40E0D0',
    'coral': '#FF7F50',
    'salmon': '#FA8072',
    'navy': '#000080',
    'maroon': '#800000',
    'olive': '#808000',
    'lime': '#00FF00',
    'aqua': '#00FFFF',
    'beige': '#F5F5DC',
    'ivory': '#FFFFF0',
    'cream': '#FFFDD0',
    'tan': '#D2B48C',
    'khaki': '#F0E68C',
    'lavender': '#E6E6FA',
    'violet': '#EE82EE',
    'indigo': '#4B0082',
    'crimson': '#DC143C',
    'scarlet': '#FF2400',
    'emerald': '#50C878',
    'jade': '#00A86B',
    'sapphire': '#0F52BA',
    'ruby': '#E0115F',
    'amber': '#FFBF00',
    # Color moods
    'warm': '#FFB347',
    'cool': '#89CFF0',
    'earthy': '#8B4513',
    'pastel': '#FFB6C1',
    'neon': '#39FF14',
    'muted': '#A9A9A9',
    'vibrant': '#FF6B6B',
    'dark': '#2F2F2F',
    'light': '#F0F0F0',
}

# Mood keywords
MOOD_KEYWORDS = [
    'happy', 'sad', 'angry', 'peaceful', 'energetic', 'calm', 'mysterious',
    'romantic', 'nostalgic', 'futuristic', 'playful', 'serious', 'whimsical',
    'dark', 'bright', 'moody', 'cheerful', 'melancholic', 'dramatic',
    'serene', 'chaotic', 'elegant', 'rustic', 'urban', 'natural',
    'professional', 'casual', 'formal', 'relaxed', 'intense', 'subtle',
]


class StyleExtractor:
    """
    Extract style elements from prompts and image metadata.

    Uses a hybrid approach:
    1. Fast keyword matching for common styles (no API cost)
    2. GPT extraction for complex/ambiguous prompts (optional)
    """

    def __init__(self, use_gpt: bool = True):
        """
        Initialize the style extractor.

        Args:
            use_gpt: Whether to use GPT for complex extraction (costs API credits)
        """
        self.use_gpt = use_gpt
        self._openai_client = None

    @property
    def openai_client(self):
        """Lazy load OpenAI client."""
        if self._openai_client is None:
            try:
                import openai
                api_key = settings.AI_PROVIDERS.get('OPENAI_API_KEY')
                if api_key:
                    self._openai_client = openai.OpenAI(api_key=api_key)
            except Exception as e:
                logger.warning(f"Could not initialize OpenAI client: {e}")
        return self._openai_client

    def extract_from_prompt(self, prompt: str, use_gpt_fallback: bool = None) -> Dict[str, Any]:
        """
        Extract style elements from a prompt.

        Args:
            prompt: The generation prompt text
            use_gpt_fallback: Override instance setting for GPT usage

        Returns:
            Dict with style_elements, color_palette, mood, and confidence
        """
        if not prompt or not prompt.strip():
            return self._empty_result()

        prompt_lower = prompt.lower()

        # Step 1: Fast keyword extraction
        styles = self._extract_style_keywords(prompt_lower)
        colors = self._extract_color_keywords(prompt_lower)
        mood = self._extract_mood(prompt_lower)

        # Calculate confidence based on matches found
        total_matches = len(styles) + len(colors) + (1 if mood else 0)

        # Step 2: If few matches and GPT enabled, use GPT for deeper analysis
        should_use_gpt = use_gpt_fallback if use_gpt_fallback is not None else self.use_gpt

        if total_matches < 2 and should_use_gpt and self.openai_client:
            gpt_result = self._extract_with_gpt(prompt)
            if gpt_result:
                # Merge GPT results with keyword results
                styles = list(set(styles + gpt_result.get('style_elements', [])))[:5]
                colors = list(set(colors + gpt_result.get('color_palette', [])))[:5]
                if not mood and gpt_result.get('mood'):
                    mood = gpt_result['mood']

        # Ensure we always have at least some values
        if not styles:
            styles = self._infer_styles_from_prompt(prompt_lower)
        if not colors:
            colors = self._infer_colors_from_context(prompt_lower)

        confidence = min(0.95, 0.3 + (len(styles) * 0.15) + (len(colors) * 0.1))

        return {
            'style_elements': styles[:5],  # Max 5 styles
            'color_palette': colors[:5],   # Max 5 colors
            'mood': mood or 'neutral',
            'confidence': confidence,
            'extraction_method': 'hybrid' if should_use_gpt else 'keyword'
        }

    def _extract_style_keywords(self, prompt_lower: str) -> List[str]:
        """Extract style keywords using fast matching."""
        found_styles = []
        for keyword, style in STYLE_KEYWORDS.items():
            if keyword in prompt_lower:
                if style not in found_styles:
                    found_styles.append(style)
        return found_styles

    def _extract_color_keywords(self, prompt_lower: str) -> List[str]:
        """Extract color keywords and return hex values."""
        found_colors = []
        for keyword, hex_color in COLOR_KEYWORDS.items():
            if keyword in prompt_lower:
                if hex_color not in found_colors:
                    found_colors.append(hex_color)
        return found_colors

    def _extract_mood(self, prompt_lower: str) -> Optional[str]:
        """Extract the primary mood from prompt."""
        for mood in MOOD_KEYWORDS:
            if mood in prompt_lower:
                return mood
        return None

    def _infer_styles_from_prompt(self, prompt_lower: str) -> List[str]:
        """Infer styles when no explicit keywords found."""
        inferred = []

        # Check for subject-based inference
        if any(word in prompt_lower for word in ['photo', 'photograph', 'camera', 'portrait']):
            inferred.append('photographic')
        elif any(word in prompt_lower for word in ['paint', 'brush', 'canvas', 'artistic']):
            inferred.append('artistic')
        elif any(word in prompt_lower for word in ['logo', 'brand', 'corporate', 'business']):
            inferred.append('professional')
        elif any(word in prompt_lower for word in ['character', 'hero', 'villain', 'creature']):
            inferred.append('character design')
        elif any(word in prompt_lower for word in ['landscape', 'nature', 'mountain', 'ocean', 'forest']):
            inferred.append('scenic')
        elif any(word in prompt_lower for word in ['product', 'item', 'object']):
            inferred.append('product photography')
        else:
            inferred.append('general')

        return inferred

    def _infer_colors_from_context(self, prompt_lower: str) -> List[str]:
        """Infer colors from contextual clues."""
        inferred = []

        # Nature-based inference
        if any(word in prompt_lower for word in ['forest', 'tree', 'grass', 'nature']):
            inferred.extend(['#228B22', '#90EE90'])  # Forest green, light green
        elif any(word in prompt_lower for word in ['ocean', 'sea', 'water', 'beach']):
            inferred.extend(['#0077BE', '#87CEEB'])  # Ocean blue, sky blue
        elif any(word in prompt_lower for word in ['sunset', 'sunrise', 'dawn', 'dusk']):
            inferred.extend(['#FF6B35', '#FFD700'])  # Orange, gold
        elif any(word in prompt_lower for word in ['night', 'dark', 'shadow']):
            inferred.extend(['#1a1a2e', '#4a4a6a'])  # Dark blue-black
        elif any(word in prompt_lower for word in ['fire', 'flame', 'burn']):
            inferred.extend(['#FF4500', '#FF6347'])  # Orange-red
        elif any(word in prompt_lower for word in ['ice', 'snow', 'winter', 'cold']):
            inferred.extend(['#E0FFFF', '#B0E0E6'])  # Light cyan, powder blue

        # If still nothing, use neutral palette
        if not inferred:
            inferred = ['#6B7280', '#9CA3AF']  # Gray tones

        return inferred

    def _extract_with_gpt(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Use GPT to extract style elements from complex prompts."""
        if not self.openai_client:
            return None

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a style analysis expert. Extract style characteristics from image generation prompts.

Return ONLY a JSON object with these fields:
- style_elements: list of 2-5 artistic style descriptors (e.g., "minimalist", "cyberpunk", "watercolor")
- color_palette: list of 2-5 hex color codes that match the prompt's mood/subject
- mood: single word describing the emotional tone

Example response:
{"style_elements": ["cinematic", "dramatic", "dark"], "color_palette": ["#1a1a2e", "#4a4a6a", "#FF6B35"], "mood": "mysterious"}"""
                    },
                    {
                        "role": "user",
                        "content": f"Extract style elements from this prompt: {prompt}"
                    }
                ],
                max_completion_tokens=200,
                reasoning_effort="low",
            )

            content = response.choices[0].message.content.strip()

            # Parse JSON from response
            # Handle potential markdown code blocks
            if '```' in content:
                content = re.search(r'```(?:json)?\s*(.*?)\s*```', content, re.DOTALL)
                if content:
                    content = content.group(1)

            return json.loads(content)

        except Exception as e:
            logger.warning(f"GPT style extraction failed: {e}")
            return None

    def _empty_result(self) -> Dict[str, Any]:
        """Return empty result structure."""
        return {
            'style_elements': [],
            'color_palette': [],
            'mood': 'neutral',
            'confidence': 0.0,
            'extraction_method': 'none'
        }

    def extract_from_image_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract style elements from image generation metadata.

        Args:
            metadata: Image metadata including model, parameters, etc.

        Returns:
            Dict with style_elements, color_palette, mood
        """
        styles = []

        # Extract from model name
        model = metadata.get('model', '').lower()
        if 'sdxl' in model:
            styles.append('SDXL quality')
        elif 'sd3' in model:
            styles.append('SD3 quality')
        elif 'ultra' in model:
            styles.append('ultra quality')

        # Extract from generation parameters
        params = metadata.get('parameters', {})

        if params.get('negative_prompt'):
            # Negative prompts can indicate desired style
            neg = params['negative_prompt'].lower()
            if 'blur' in neg:
                styles.append('sharp')
            if 'noise' in neg:
                styles.append('clean')

        # Aspect ratio can indicate style
        aspect = params.get('aspect_ratio', '')
        if '16:9' in aspect:
            styles.append('cinematic')
        elif '9:16' in aspect:
            styles.append('portrait')
        elif '1:1' in aspect:
            styles.append('square')

        return {
            'style_elements': styles[:5],
            'color_palette': [],
            'mood': 'neutral',
            'confidence': 0.5 if styles else 0.2,
            'extraction_method': 'metadata'
        }


# Global instance for easy access
style_extractor = StyleExtractor(use_gpt=True)


def extract_styles(prompt: str, metadata: Optional[Dict] = None, use_gpt: bool = True) -> Dict[str, Any]:
    """
    Convenience function to extract styles from prompt and/or metadata.

    Args:
        prompt: The generation prompt
        metadata: Optional image metadata
        use_gpt: Whether to use GPT for complex extraction

    Returns:
        Combined style extraction result
    """
    extractor = StyleExtractor(use_gpt=use_gpt)

    # Extract from prompt
    result = extractor.extract_from_prompt(prompt)

    # Merge metadata extraction if available
    if metadata:
        meta_result = extractor.extract_from_image_metadata(metadata)
        # Combine styles (prompt takes priority)
        combined_styles = list(set(result['style_elements'] + meta_result['style_elements']))[:5]
        result['style_elements'] = combined_styles
        # Boost confidence if metadata adds info
        if meta_result['style_elements']:
            result['confidence'] = min(0.95, result['confidence'] + 0.1)

    return result

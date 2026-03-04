"""
CivitAI Spider - Stable Diffusion Models & LoRA Intelligence
=============================================================

Session 534: Simplified to work with spider network interface.
Uses Civitai public API to fetch trending models, LoRAs, and embeddings.
"""

from ai_core.spiders.web_request_layer import cached_get
import logging
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class CivitAISpider:
    """CivitAI spider - trending SD models, LoRAs, and embeddings"""

    name = "civitai"

    BASE_URL = "https://civitai.com/api/v1"

    # Model types to fetch
    MODEL_TYPES = [
        'Checkpoint',
        'LORA',
        'TextualInversion',
        'Controlnet',
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch trending models from Civitai API.

        Args:
            max_results: Maximum number of models to fetch

        Returns:
            List of model dictionaries
        """
        all_items = []

        # Fetch trending models
        try:
            models = self._fetch_models(limit=max_results)
            all_items.extend(models)
        except Exception as e:
            logger.warning(f"Error fetching Civitai models: {e}")

        # If API fails, return curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Civitai spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_models(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch trending models from Civitai API."""
        items = []

        try:
            # Fetch models sorted by rating/downloads
            url = f"{self.BASE_URL}/models"
            params = {
                'limit': min(limit, 100),  # API max is 100
                'sort': 'Highest Rated',
                'period': 'Week',
                'nsfw': 'false',  # SFW only
            }

            response = cached_get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            models = data.get('items', [])

            for model in models:
                model_id = model.get('id')
                name = model.get('name', '')
                if not name:
                    continue

                model_type = model.get('type', 'Model')
                creator = model.get('creator', {}).get('username', 'Unknown')
                description = model.get('description', '') or ''

                # Get stats
                stats = model.get('stats', {})
                downloads = stats.get('downloadCount', 0)
                rating = stats.get('rating', 0)
                favorites = stats.get('favoriteCount', 0)

                # Build description
                desc = f"{model_type}: {name}. "
                if description:
                    # Clean HTML from description
                    import re
                    clean_desc = re.sub(r'<[^>]+>', '', description)[:300]
                    desc += f"{clean_desc} "
                desc += f"Downloads: {downloads:,}. Rating: {rating:.1f}/5."

                # Get tags
                tags = model.get('tags', [])

                # Get preview image
                model_versions = model.get('modelVersions', [])
                preview_url = ''
                if model_versions:
                    images = model_versions[0].get('images', [])
                    if images:
                        preview_url = images[0].get('url', '')

                items.append({
                    'title': name,
                    'name': name,
                    'url': f"https://civitai.com/models/{model_id}",
                    'link': f"https://civitai.com/models/{model_id}",
                    'summary': desc,
                    'description': desc,
                    'author': creator,
                    'model_type': model_type,
                    'downloads': downloads,
                    'rating': rating,
                    'favorites': favorites,
                    'image_url': preview_url,
                    'category': model_type.lower(),
                    'source': 'Civitai',
                    'data_type': 'sd_model',
                    'tags': ['ai', 'stable-diffusion', model_type.lower()] + tags[:5],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error fetching Civitai models: {e}")

        return items

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated SD/AI art topics when API fails."""
        topics = [
            ('SDXL Checkpoints', 'checkpoint', 'Base models for SDXL image generation.'),
            ('Realistic LoRAs', 'lora', 'Fine-tuned LoRAs for realistic portraits and photos.'),
            ('Anime LoRAs', 'lora', 'LoRAs for anime and manga-style generation.'),
            ('Character LoRAs', 'lora', 'LoRAs trained on specific characters.'),
            ('Style LoRAs', 'lora', 'LoRAs for artistic styles and aesthetics.'),
            ('ControlNet Models', 'controlnet', 'Models for pose, depth, and edge control.'),
            ('Textual Inversions', 'embedding', 'Embeddings for concepts and styles.'),
            ('Negative Embeddings', 'embedding', 'Embeddings for quality improvement.'),
            ('Pony Diffusion', 'checkpoint', 'Specialized anime/furry base models.'),
            ('Flux Models', 'checkpoint', 'Next-generation diffusion models.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://civitai.com/models?types={category}',
                'link': f'https://civitai.com/models?types={category}',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'Civitai',
                'data_type': 'sd_topic',
                'tags': ['ai', 'stable-diffusion', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]

"""
HuggingFace Spider - AI/ML Model & Dataset Intelligence
========================================================

Session 534: Simplified to work with spider network interface.
Uses HuggingFace Hub API to track trending models and datasets.
"""

from ai_core.spiders.web_request_layer import cached_get
import logging
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class HuggingFaceSpider:
    """HuggingFace spider - trending AI/ML models and datasets"""

    name = "huggingface"

    BASE_URL = "https://huggingface.co/api"

    # Model tasks to track
    MODEL_TASKS = [
        'text-generation',
        'text-to-image',
        'image-to-text',
        'automatic-speech-recognition',
        'text-classification',
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch trending models and datasets from HuggingFace Hub.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of model/dataset dictionaries
        """
        all_items = []

        # Fetch trending models
        try:
            models = self._fetch_models(limit=max_results // 2)
            all_items.extend(models)
        except Exception as e:
            logger.warning(f"Error fetching HuggingFace models: {e}")

        # Fetch trending datasets
        try:
            datasets = self._fetch_datasets(limit=max_results // 4)
            all_items.extend(datasets)
        except Exception as e:
            logger.warning(f"Error fetching HuggingFace datasets: {e}")

        # Fetch trending spaces
        try:
            spaces = self._fetch_spaces(limit=max_results // 4)
            all_items.extend(spaces)
        except Exception as e:
            logger.warning(f"Error fetching HuggingFace spaces: {e}")

        # If API fails, return curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"HuggingFace spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_models(self, limit: int = 25) -> List[Dict[str, Any]]:
        """Fetch trending models from HuggingFace."""
        items = []

        try:
            # Fetch models sorted by trending/downloads
            url = f"{self.BASE_URL}/models"
            params = {
                'sort': 'trending',
                'direction': -1,
                'limit': limit,
            }

            response = cached_get(url, params=params, timeout=15)
            response.raise_for_status()
            models = response.json()

            for model in models:
                model_id = model.get('modelId', model.get('id', ''))
                if not model_id:
                    continue

                # Get task/pipeline tag
                pipeline_tag = model.get('pipeline_tag', 'unknown')
                tags = model.get('tags', [])

                # Build description
                description = f"AI model for {pipeline_tag}. "
                if model.get('downloads'):
                    description += f"Downloads: {model.get('downloads'):,}. "
                if model.get('likes'):
                    description += f"Likes: {model.get('likes'):,}."

                items.append({
                    'title': model_id,
                    'name': model_id,
                    'url': f"https://huggingface.co/{model_id}",
                    'link': f"https://huggingface.co/{model_id}",
                    'summary': description,
                    'description': description,
                    'author': model_id.split('/')[0] if '/' in model_id else 'HuggingFace',
                    'pipeline_tag': pipeline_tag,
                    'downloads': model.get('downloads', 0),
                    'likes': model.get('likes', 0),
                    'category': 'model',
                    'source': 'HuggingFace',
                    'data_type': 'ai_model',
                    'tags': ['ai', 'ml', 'model', pipeline_tag] + tags[:3],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error fetching HuggingFace models: {e}")

        return items

    def _fetch_datasets(self, limit: int = 15) -> List[Dict[str, Any]]:
        """Fetch trending datasets from HuggingFace."""
        items = []

        try:
            url = f"{self.BASE_URL}/datasets"
            params = {
                'sort': 'trending',
                'direction': -1,
                'limit': limit,
            }

            response = cached_get(url, params=params, timeout=15)
            response.raise_for_status()
            datasets = response.json()

            for ds in datasets:
                ds_id = ds.get('id', '')
                if not ds_id:
                    continue

                description = f"Dataset: {ds_id}. "
                if ds.get('downloads'):
                    description += f"Downloads: {ds.get('downloads'):,}."

                items.append({
                    'title': ds_id,
                    'name': ds_id,
                    'url': f"https://huggingface.co/datasets/{ds_id}",
                    'link': f"https://huggingface.co/datasets/{ds_id}",
                    'summary': description,
                    'description': description,
                    'author': ds_id.split('/')[0] if '/' in ds_id else 'HuggingFace',
                    'downloads': ds.get('downloads', 0),
                    'likes': ds.get('likes', 0),
                    'category': 'dataset',
                    'source': 'HuggingFace',
                    'data_type': 'ai_dataset',
                    'tags': ['ai', 'ml', 'dataset', 'training'],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error fetching HuggingFace datasets: {e}")

        return items

    def _fetch_spaces(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch trending spaces (demos) from HuggingFace."""
        items = []

        try:
            url = f"{self.BASE_URL}/spaces"
            params = {
                'sort': 'trending',
                'direction': -1,
                'limit': limit,
            }

            response = cached_get(url, params=params, timeout=15)
            response.raise_for_status()
            spaces = response.json()

            for space in spaces:
                space_id = space.get('id', '')
                if not space_id:
                    continue

                sdk = space.get('sdk', 'gradio')
                description = f"AI demo/app using {sdk}. "
                if space.get('likes'):
                    description += f"Likes: {space.get('likes'):,}."

                items.append({
                    'title': space_id,
                    'name': space_id,
                    'url': f"https://huggingface.co/spaces/{space_id}",
                    'link': f"https://huggingface.co/spaces/{space_id}",
                    'summary': description,
                    'description': description,
                    'author': space_id.split('/')[0] if '/' in space_id else 'HuggingFace',
                    'sdk': sdk,
                    'likes': space.get('likes', 0),
                    'category': 'space',
                    'source': 'HuggingFace',
                    'data_type': 'ai_demo',
                    'tags': ['ai', 'ml', 'demo', 'app', sdk],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error fetching HuggingFace spaces: {e}")

        return items

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated AI/ML topics when API fails."""
        topics = [
            ('Text Generation Models', 'text-generation', 'LLMs for text generation like Llama, Mistral, GPT.'),
            ('Image Generation Models', 'text-to-image', 'Stable Diffusion, FLUX, and other image generators.'),
            ('Speech Recognition', 'asr', 'Whisper and other speech-to-text models.'),
            ('Vision Models', 'image-to-text', 'Image captioning and visual understanding models.'),
            ('Embedding Models', 'embedding', 'Text and image embedding models for search and RAG.'),
            ('Fine-tuning Datasets', 'dataset', 'Popular datasets for training and fine-tuning.'),
            ('AI Demo Spaces', 'space', 'Interactive AI demos and applications.'),
            ('LoRA Adapters', 'lora', 'Low-rank adaptation models for efficient fine-tuning.'),
            ('Multimodal Models', 'multimodal', 'Models combining text, image, and audio.'),
            ('Code Generation', 'code', 'AI models for code generation and completion.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://huggingface.co/models?pipeline_tag={category}',
                'link': f'https://huggingface.co/models?pipeline_tag={category}',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'HuggingFace',
                'data_type': 'ai_topic',
                'tags': ['ai', 'ml', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]

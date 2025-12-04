"""
HuggingFace Spider - AI/ML Model & Dataset Intelligence
========================================================

Session 343: Spider for HuggingFace Hub API to track AI/ML trends.
Collects trending models, datasets, and spaces.

Uses HUGGING_FACE_API from environment for authenticated requests.
HuggingFace Hub API is largely free and doesn't require auth for basic queries.
"""

import aiohttp
import asyncio
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class HuggingFaceSpider(BaseIntelligenceSpider):
    """HuggingFace spider - trending models, datasets, and AI/ML spaces"""

    BASE_URL = "https://huggingface.co/api"

    # Model types of interest
    MODEL_TASKS = [
        'text-generation',
        'image-to-text',
        'text-to-image',
        'automatic-speech-recognition',
        'text-to-speech',
        'text-classification',
        'question-answering',
        'summarization',
        'translation',
        'feature-extraction',
    ]

    # Popular model architectures to track
    ARCHITECTURES = [
        'llama',
        'mistral',
        'phi',
        'gemma',
        'qwen',
        'stable-diffusion',
        'flux',
        'whisper',
    ]

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)
        self.api_key = os.getenv('HUGGING_FACE_API', '')

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch HuggingFace trending data"""
        try:
            all_models = []
            all_datasets = []
            all_spaces = []

            headers = {}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'

            async with aiohttp.ClientSession() as session:
                # Fetch trending models
                try:
                    models_url = f"{self.BASE_URL}/models"
                    params = {
                        'sort': 'downloads',
                        'direction': '-1',
                        'limit': 30,
                    }

                    async with session.get(models_url, headers=headers, params=params, timeout=15) as response:
                        if response.status == 200:
                            models = await response.json()

                            for model in models:
                                all_models.append({
                                    'id': model.get('id', ''),
                                    'modelId': model.get('modelId', ''),
                                    'author': model.get('author', ''),
                                    'downloads': model.get('downloads', 0),
                                    'likes': model.get('likes', 0),
                                    'pipeline_tag': model.get('pipeline_tag', ''),
                                    'tags': model.get('tags', [])[:10],
                                    'created_at': model.get('createdAt', ''),
                                    'last_modified': model.get('lastModified', ''),
                                    'library_name': model.get('library_name', ''),
                                    'url': f"https://huggingface.co/{model.get('id', '')}",
                                    'source': 'huggingface',
                                    'type': 'model',
                                })
                        else:
                            self.logger.warning(f"HuggingFace models API returned {response.status}")

                except Exception as e:
                    self.logger.warning(f"Error fetching models: {e}")

                await asyncio.sleep(0.5)

                # Fetch trending datasets
                try:
                    datasets_url = f"{self.BASE_URL}/datasets"
                    params = {
                        'sort': 'downloads',
                        'direction': '-1',
                        'limit': 20,
                    }

                    async with session.get(datasets_url, headers=headers, params=params, timeout=15) as response:
                        if response.status == 200:
                            datasets = await response.json()

                            for dataset in datasets:
                                all_datasets.append({
                                    'id': dataset.get('id', ''),
                                    'author': dataset.get('author', ''),
                                    'downloads': dataset.get('downloads', 0),
                                    'likes': dataset.get('likes', 0),
                                    'tags': dataset.get('tags', [])[:10],
                                    'created_at': dataset.get('createdAt', ''),
                                    'url': f"https://huggingface.co/datasets/{dataset.get('id', '')}",
                                    'source': 'huggingface',
                                    'type': 'dataset',
                                })
                        else:
                            self.logger.warning(f"HuggingFace datasets API returned {response.status}")

                except Exception as e:
                    self.logger.warning(f"Error fetching datasets: {e}")

                await asyncio.sleep(0.5)

                # Fetch trending spaces (demos)
                try:
                    spaces_url = f"{self.BASE_URL}/spaces"
                    params = {
                        'sort': 'likes',
                        'direction': '-1',
                        'limit': 20,
                    }

                    async with session.get(spaces_url, headers=headers, params=params, timeout=15) as response:
                        if response.status == 200:
                            spaces = await response.json()

                            for space in spaces:
                                all_spaces.append({
                                    'id': space.get('id', ''),
                                    'author': space.get('author', ''),
                                    'likes': space.get('likes', 0),
                                    'sdk': space.get('sdk', ''),
                                    'tags': space.get('tags', [])[:10],
                                    'created_at': space.get('createdAt', ''),
                                    'url': f"https://huggingface.co/spaces/{space.get('id', '')}",
                                    'source': 'huggingface',
                                    'type': 'space',
                                })
                        else:
                            self.logger.warning(f"HuggingFace spaces API returned {response.status}")

                except Exception as e:
                    self.logger.warning(f"Error fetching spaces: {e}")

                # Fetch models by specific tasks
                for task in self.MODEL_TASKS[:3]:  # Limit to avoid rate limits
                    try:
                        task_url = f"{self.BASE_URL}/models"
                        params = {
                            'filter': task,
                            'sort': 'downloads',
                            'direction': '-1',
                            'limit': 10,
                        }

                        async with session.get(task_url, headers=headers, params=params, timeout=10) as response:
                            if response.status == 200:
                                models = await response.json()
                                for model in models:
                                    model_data = {
                                        'id': model.get('id', ''),
                                        'modelId': model.get('modelId', ''),
                                        'author': model.get('author', ''),
                                        'downloads': model.get('downloads', 0),
                                        'likes': model.get('likes', 0),
                                        'pipeline_tag': model.get('pipeline_tag', ''),
                                        'task': task,
                                        'url': f"https://huggingface.co/{model.get('id', '')}",
                                        'source': 'huggingface',
                                        'type': 'model',
                                    }
                                    # Avoid duplicates
                                    if model_data['id'] not in [m['id'] for m in all_models]:
                                        all_models.append(model_data)

                        await asyncio.sleep(0.3)

                    except Exception as e:
                        self.logger.warning(f"Error fetching {task} models: {e}")

            return {
                'models': all_models,
                'datasets': all_datasets,
                'spaces': all_spaces,
                'source': 'huggingface'
            }

        except Exception as e:
            self.logger.error(f"Error fetching HuggingFace data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process HuggingFace data into intelligence"""
        try:
            models = raw_data.get('models', [])
            datasets = raw_data.get('datasets', [])
            spaces = raw_data.get('spaces', [])

            # Analyze model types/tasks
            task_stats = {}
            for model in models:
                task = model.get('pipeline_tag', 'other') or 'other'
                if task not in task_stats:
                    task_stats[task] = {'count': 0, 'total_downloads': 0}
                task_stats[task]['count'] += 1
                task_stats[task]['total_downloads'] += model.get('downloads', 0)

            # Top models by downloads
            top_models = sorted(models, key=lambda x: x.get('downloads', 0), reverse=True)[:15]

            # Extract trending tags
            all_tags = []
            for model in models:
                all_tags.extend(model.get('tags', []))
            tag_frequency = {}
            for tag in all_tags:
                tag_frequency[tag] = tag_frequency.get(tag, 0) + 1
            trending_tags = sorted(tag_frequency.items(), key=lambda x: x[1], reverse=True)[:30]

            # Popular libraries
            library_stats = {}
            for model in models:
                lib = model.get('library_name', 'unknown') or 'unknown'
                library_stats[lib] = library_stats.get(lib, 0) + 1

            # SDK usage in spaces
            sdk_stats = {}
            for space in spaces:
                sdk = space.get('sdk', 'unknown') or 'unknown'
                sdk_stats[sdk] = sdk_stats.get(sdk, 0) + 1

            content = {
                'models': models,
                'datasets': datasets,
                'spaces': spaces,
                'top_models': top_models,
                'task_stats': task_stats,
                'trending_tags': trending_tags,
                'library_stats': library_stats,
                'sdk_stats': sdk_stats,
                'total_models': len(models),
                'total_datasets': len(datasets),
                'total_spaces': len(spaces),
                'total_downloads': sum(m.get('downloads', 0) for m in models),
            }

            quality_score = min(1.0, (len(models) + len(datasets) + len(spaces)) / 60 + 0.3)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='huggingface.co',
                data_type='ai_ml_intelligence',
                content=content,
                metadata={
                    'model_count': len(models),
                    'dataset_count': len(datasets),
                    'space_count': len(spaces),
                    'top_tasks': list(task_stats.keys())[:5],
                    'source': 'huggingface',
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['huggingface', 'ai', 'ml', 'models', 'datasets', 'llm', 'transformers'],
                target_agents=['research_agent', 'trend_analysis_agent', 'competitor_analysis_agent'],
                target_advisors=['ai_advisor', 'tech_strategist', 'innovation_advisor']
            )

        except Exception as e:
            self.logger.error(f"Error processing HuggingFace data: {e}")
            return None

    def get_required_fields(self) -> List[str]:
        return ['id', 'downloads']

    def get_relevance_keywords(self) -> List[str]:
        return ['huggingface', 'model', 'dataset', 'ai', 'ml', 'llm', 'transformers', 'diffusion']

"""
Kaggle Spider - ML Competition & Dataset Intelligence
======================================================

Session 452: Spider for Kaggle API to track ML trends, competitions, and datasets.
Complements HuggingFace spider for comprehensive ML intelligence.

Uses KAGGLE_USERNAME and KAGGLE_KEY from environment for authenticated requests.
Kaggle API requires authentication for all endpoints.

Data collected:
- Trending/popular datasets
- Active and recent competitions
- Popular notebooks/kernels
- Prize pools and deadlines
"""

import aiohttp
import asyncio
import os
import base64
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class KaggleSpider(BaseIntelligenceSpider):
    """Kaggle spider - competitions, datasets, and ML trends"""

    BASE_URL = "https://www.kaggle.com/api/v1"

    # Dataset categories of interest
    DATASET_TAGS = [
        'computer-vision',
        'nlp',
        'tabular',
        'time-series',
        'image-data',
        'text-data',
        'audio-data',
        'geospatial-data',
    ]

    # Competition categories
    COMPETITION_CATEGORIES = [
        'featured',
        'research',
        'getting-started',
        'playground',
    ]

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)
        self.kaggle_username = os.getenv('KAGGLE_USERNAME', '')
        # Session 503: Support KAGGLE_API_TOKEN (official), KAGGLE_API_KEY, and KAGGLE_KEY (legacy)
        self.kaggle_key = os.getenv('KAGGLE_API_TOKEN', os.getenv('KAGGLE_API_KEY', os.getenv('KAGGLE_KEY', '')))

    def _get_auth_header(self) -> Dict[str, str]:
        """Generate auth header for Kaggle API"""
        if self.kaggle_key:
            # Session 503: New KGAT_* tokens use Bearer auth, old tokens use Basic auth
            if self.kaggle_key.startswith('KGAT_'):
                return {'Authorization': f'Bearer {self.kaggle_key}'}
            elif self.kaggle_username:
                # Legacy Basic auth for old-style keys
                credentials = f"{self.kaggle_username}:{self.kaggle_key}"
                encoded = base64.b64encode(credentials.encode()).decode()
                return {'Authorization': f'Basic {encoded}'}
        return {}

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch Kaggle trending data"""
        try:
            all_competitions = []
            all_datasets = []
            all_kernels = []

            headers = self._get_auth_header()

            if not headers:
                self.logger.warning("Kaggle credentials not configured. Set KAGGLE_USERNAME and KAGGLE_KEY.")
                return self._create_mock_data()

            async with aiohttp.ClientSession() as session:
                # Fetch active competitions
                try:
                    competitions_url = f"{self.BASE_URL}/competitions/list"
                    params = {
                        'sortBy': 'recentlyCreated',
                        'page': 1,
                        'pageSize': 20,
                    }

                    async with session.get(competitions_url, headers=headers, params=params, timeout=15) as response:
                        if response.status == 200:
                            competitions = await response.json()
                            for comp in competitions[:15]:
                                all_competitions.append({
                                    'id': comp.get('ref', comp.get('id', '')),
                                    'title': comp.get('title', ''),
                                    'category': comp.get('category', ''),
                                    'reward': comp.get('reward', ''),
                                    'deadline': comp.get('deadline', ''),
                                    'teams_count': comp.get('teamCount', 0),
                                    'description': comp.get('description', '')[:200] if comp.get('description') else '',
                                    'url': f"https://www.kaggle.com/c/{comp.get('ref', '')}",
                                    'tags': comp.get('tags', []),
                                })
                        else:
                            self.logger.warning(f"Kaggle competitions API returned {response.status}")
                except Exception as e:
                    self.logger.error(f"Error fetching Kaggle competitions: {e}")

                # Fetch trending datasets
                try:
                    datasets_url = f"{self.BASE_URL}/datasets/list"
                    params = {
                        'sortBy': 'hottest',
                        'page': 1,
                        'pageSize': 20,
                    }

                    async with session.get(datasets_url, headers=headers, params=params, timeout=15) as response:
                        if response.status == 200:
                            datasets = await response.json()
                            for ds in datasets[:15]:
                                all_datasets.append({
                                    'id': ds.get('ref', ds.get('id', '')),
                                    'title': ds.get('title', ''),
                                    'owner': ds.get('ownerName', ds.get('creatorName', '')),
                                    'size': ds.get('totalBytes', 0),
                                    'downloads': ds.get('downloadCount', 0),
                                    'votes': ds.get('voteCount', 0),
                                    'usability': ds.get('usabilityRating', 0),
                                    'description': ds.get('subtitle', '')[:200] if ds.get('subtitle') else '',
                                    'url': f"https://www.kaggle.com/datasets/{ds.get('ref', '')}",
                                    'tags': ds.get('tags', []),
                                    'last_updated': ds.get('lastUpdated', ''),
                                })
                        else:
                            self.logger.warning(f"Kaggle datasets API returned {response.status}")
                except Exception as e:
                    self.logger.error(f"Error fetching Kaggle datasets: {e}")

                # Fetch trending kernels/notebooks
                try:
                    kernels_url = f"{self.BASE_URL}/kernels/list"
                    params = {
                        'sortBy': 'hotness',
                        'page': 1,
                        'pageSize': 20,
                    }

                    async with session.get(kernels_url, headers=headers, params=params, timeout=15) as response:
                        if response.status == 200:
                            kernels = await response.json()
                            for kernel in kernels[:15]:
                                all_kernels.append({
                                    'id': kernel.get('ref', kernel.get('id', '')),
                                    'title': kernel.get('title', ''),
                                    'author': kernel.get('author', ''),
                                    'votes': kernel.get('totalVotes', 0),
                                    'language': kernel.get('language', ''),
                                    'kernel_type': kernel.get('kernelType', ''),
                                    'url': f"https://www.kaggle.com/code/{kernel.get('ref', '')}",
                                    'competition': kernel.get('competitionDataSources', []),
                                    'dataset': kernel.get('datasetDataSources', []),
                                })
                        else:
                            self.logger.warning(f"Kaggle kernels API returned {response.status}")
                except Exception as e:
                    self.logger.error(f"Error fetching Kaggle kernels: {e}")

            return {
                'competitions': all_competitions,
                'datasets': all_datasets,
                'kernels': all_kernels,
                'fetched_at': datetime.now(timezone.utc).isoformat(),
                'source': 'kaggle_api',
            }

        except Exception as e:
            self.logger.error(f"Kaggle spider error: {e}")
            return None

    def _create_mock_data(self) -> Dict[str, Any]:
        """Create mock data when credentials aren't available"""
        return {
            'competitions': [
                {
                    'id': 'mock-competition',
                    'title': 'Configure KAGGLE_USERNAME and KAGGLE_KEY for real data',
                    'category': 'featured',
                    'reward': '$0',
                    'teams_count': 0,
                    'url': 'https://www.kaggle.com',
                    'description': 'Set up Kaggle API credentials to fetch real competition data',
                }
            ],
            'datasets': [],
            'kernels': [],
            'fetched_at': datetime.now(timezone.utc).isoformat(),
            'source': 'mock',
            'note': 'Configure KAGGLE_USERNAME and KAGGLE_KEY environment variables',
        }

    def transform_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> List[IntelligenceData]:
        """Transform Kaggle data into intelligence format"""
        intelligence_items = []

        if not raw_data:
            return intelligence_items

        # Transform competitions
        for comp in raw_data.get('competitions', []):
            intelligence_items.append(IntelligenceData(
                source='kaggle',
                category='ml_competition',
                title=comp.get('title', 'Unknown Competition'),
                content=f"Competition: {comp.get('title')}\n"
                        f"Category: {comp.get('category', 'N/A')}\n"
                        f"Reward: {comp.get('reward', 'N/A')}\n"
                        f"Teams: {comp.get('teams_count', 0)}\n"
                        f"Deadline: {comp.get('deadline', 'N/A')}\n"
                        f"{comp.get('description', '')}",
                url=comp.get('url', ''),
                metadata={
                    'type': 'competition',
                    'category': comp.get('category'),
                    'reward': comp.get('reward'),
                    'teams_count': comp.get('teams_count'),
                    'deadline': comp.get('deadline'),
                    'tags': comp.get('tags', []),
                },
                timestamp=datetime.now(timezone.utc),
                relevance_score=min(1.0, comp.get('teams_count', 0) / 1000 + 0.5),
            ))

        # Transform datasets
        for ds in raw_data.get('datasets', []):
            # Calculate relevance based on downloads and votes
            downloads = ds.get('downloads', 0)
            votes = ds.get('votes', 0)
            usability = ds.get('usability', 0)
            relevance = min(1.0, (downloads / 10000) + (votes / 100) + (usability / 10))

            intelligence_items.append(IntelligenceData(
                source='kaggle',
                category='ml_dataset',
                title=ds.get('title', 'Unknown Dataset'),
                content=f"Dataset: {ds.get('title')}\n"
                        f"Owner: {ds.get('owner', 'N/A')}\n"
                        f"Downloads: {downloads:,}\n"
                        f"Votes: {votes}\n"
                        f"Usability: {usability}/10\n"
                        f"{ds.get('description', '')}",
                url=ds.get('url', ''),
                metadata={
                    'type': 'dataset',
                    'owner': ds.get('owner'),
                    'downloads': downloads,
                    'votes': votes,
                    'usability': usability,
                    'size_bytes': ds.get('size', 0),
                    'tags': ds.get('tags', []),
                    'last_updated': ds.get('last_updated'),
                },
                timestamp=datetime.now(timezone.utc),
                relevance_score=relevance,
            ))

        # Transform kernels/notebooks
        for kernel in raw_data.get('kernels', []):
            votes = kernel.get('votes', 0)
            relevance = min(1.0, votes / 100 + 0.3)

            intelligence_items.append(IntelligenceData(
                source='kaggle',
                category='ml_notebook',
                title=kernel.get('title', 'Unknown Notebook'),
                content=f"Notebook: {kernel.get('title')}\n"
                        f"Author: {kernel.get('author', 'N/A')}\n"
                        f"Votes: {votes}\n"
                        f"Language: {kernel.get('language', 'N/A')}\n"
                        f"Type: {kernel.get('kernel_type', 'N/A')}",
                url=kernel.get('url', ''),
                metadata={
                    'type': 'kernel',
                    'author': kernel.get('author'),
                    'votes': votes,
                    'language': kernel.get('language'),
                    'kernel_type': kernel.get('kernel_type'),
                    'competition_sources': kernel.get('competition', []),
                    'dataset_sources': kernel.get('dataset', []),
                },
                timestamp=datetime.now(timezone.utc),
                relevance_score=relevance,
            ))

        return intelligence_items

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional['IntelligenceData']:
        """Process Kaggle raw data into a single IntelligenceData object."""
        try:
            from ai_core.spiders.base_spider import IntelligenceData as BaseIntelligenceData

            competitions = raw_data.get('competitions', [])
            datasets = raw_data.get('datasets', [])
            kernels = raw_data.get('kernels', [])

            # Build summary content
            summary_parts = []

            if competitions:
                top_comps = competitions[:5]
                comp_summary = "Top Competitions:\n" + "\n".join(
                    f"- {c.get('title', 'Unknown')} ({c.get('reward', 'N/A')})"
                    for c in top_comps
                )
                summary_parts.append(comp_summary)

            if datasets:
                top_datasets = sorted(datasets, key=lambda x: x.get('downloads', 0), reverse=True)[:5]
                ds_summary = "Trending Datasets:\n" + "\n".join(
                    f"- {d.get('title', 'Unknown')} ({d.get('downloads', 0):,} downloads)"
                    for d in top_datasets
                )
                summary_parts.append(ds_summary)

            if kernels:
                top_kernels = sorted(kernels, key=lambda x: x.get('votes', 0), reverse=True)[:5]
                kernel_summary = "Popular Notebooks:\n" + "\n".join(
                    f"- {k.get('title', 'Unknown')} ({k.get('votes', 0)} votes)"
                    for k in top_kernels
                )
                summary_parts.append(kernel_summary)

            content = "\n\n".join(summary_parts) if summary_parts else "No Kaggle data available"

            return BaseIntelligenceData(
                spider_id=self.spider_id,
                source_url='kaggle.com',
                data_type='ml_trends',
                content={
                    'summary': content,
                    'competitions_count': len(competitions),
                    'datasets_count': len(datasets),
                    'kernels_count': len(kernels),
                    'competitions': competitions[:10],
                    'datasets': datasets[:10],
                    'kernels': kernels[:10],
                },
                quality_score=0.9 if raw_data.get('source') != 'mock' else 0.3,
                metadata={
                    'source': raw_data.get('source', 'unknown'),
                    'fetched_at': raw_data.get('fetched_at'),
                }
            )

        except Exception as e:
            self.logger.error(f"Error processing Kaggle data: {e}")
            return None

    async def analyze_trends(self, data: List[IntelligenceData]) -> Dict[str, Any]:
        """Analyze Kaggle trends from collected data"""
        if not data:
            return {'error': 'No data to analyze'}

        competitions = [d for d in data if d.metadata.get('type') == 'competition']
        datasets = [d for d in data if d.metadata.get('type') == 'dataset']
        kernels = [d for d in data if d.metadata.get('type') == 'kernel']

        # Analyze competition categories
        comp_categories = {}
        for comp in competitions:
            cat = comp.metadata.get('category', 'other')
            comp_categories[cat] = comp_categories.get(cat, 0) + 1

        # Analyze popular dataset tags
        dataset_tags = {}
        for ds in datasets:
            for tag in ds.metadata.get('tags', []):
                if isinstance(tag, dict):
                    tag = tag.get('name', str(tag))
                dataset_tags[tag] = dataset_tags.get(tag, 0) + 1

        # Analyze notebook languages
        kernel_languages = {}
        for kernel in kernels:
            lang = kernel.metadata.get('language', 'unknown')
            kernel_languages[lang] = kernel_languages.get(lang, 0) + 1

        # Top datasets by downloads
        top_datasets = sorted(
            datasets,
            key=lambda x: x.metadata.get('downloads', 0),
            reverse=True
        )[:5]

        return {
            'total_items': len(data),
            'competitions_count': len(competitions),
            'datasets_count': len(datasets),
            'kernels_count': len(kernels),
            'competition_categories': comp_categories,
            'popular_dataset_tags': dict(sorted(dataset_tags.items(), key=lambda x: x[1], reverse=True)[:10]),
            'kernel_languages': kernel_languages,
            'top_datasets': [
                {
                    'title': ds.title,
                    'downloads': ds.metadata.get('downloads', 0),
                    'url': ds.url,
                }
                for ds in top_datasets
            ],
            'analyzed_at': datetime.now(timezone.utc).isoformat(),
        }

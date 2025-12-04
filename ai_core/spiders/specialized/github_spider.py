"""
GitHub Spider - Developer Trends & Open Source Intelligence
============================================================

Session 343: Spider for GitHub API to track developer trends.
Collects trending repos, topics, and developer activity.

Uses GITHUB_TOKEN from environment for authenticated requests.
"""

import aiohttp
import asyncio
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class GitHubSpider(BaseIntelligenceSpider):
    """GitHub spider - trending repos, topics, and developer activity"""

    BASE_URL = "https://api.github.com"

    # Topics of interest
    TOPICS = [
        'artificial-intelligence',
        'machine-learning',
        'generative-ai',
        'llm',
        'stable-diffusion',
        'react',
        'python',
        'typescript',
        'rust',
        'golang',
    ]

    # Search queries for trending
    SEARCH_QUERIES = [
        'stars:>1000 pushed:>2024-01-01',  # Popular active repos
        'topic:ai created:>2024-06-01',     # New AI repos
        'topic:llm stars:>100',             # LLM projects
    ]

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)
        self.token = os.getenv('GITHUB_TOKEN', '')

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch trending GitHub data"""
        try:
            all_repos = []
            trending_topics = []

            headers = {
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'DonkeyBetz-Spider/1.0'
            }
            if self.token:
                headers['Authorization'] = f'token {self.token}'

            async with aiohttp.ClientSession() as session:
                # Fetch trending repos via search
                search_url = f"{self.BASE_URL}/search/repositories"

                for query in self.SEARCH_QUERIES[:2]:  # Limit queries
                    try:
                        params = {
                            'q': query,
                            'sort': 'stars',
                            'order': 'desc',
                            'per_page': 20
                        }

                        async with session.get(search_url, headers=headers, params=params, timeout=15) as response:
                            if response.status == 200:
                                data = await response.json()
                                repos = data.get('items', [])

                                for repo in repos:
                                    all_repos.append({
                                        'name': repo.get('full_name', ''),
                                        'description': repo.get('description', ''),
                                        'url': repo.get('html_url', ''),
                                        'stars': repo.get('stargazers_count', 0),
                                        'forks': repo.get('forks_count', 0),
                                        'watchers': repo.get('watchers_count', 0),
                                        'language': repo.get('language', ''),
                                        'topics': repo.get('topics', []),
                                        'created_at': repo.get('created_at', ''),
                                        'updated_at': repo.get('updated_at', ''),
                                        'open_issues': repo.get('open_issues_count', 0),
                                        'license': repo.get('license', {}).get('name', '') if repo.get('license') else '',
                                        'source': 'github',
                                        'type': 'repository',
                                    })
                            elif response.status == 403:
                                self.logger.warning("GitHub rate limit hit")
                                break
                            else:
                                self.logger.warning(f"GitHub API returned {response.status}")

                        await asyncio.sleep(1)  # Rate limit protection

                    except Exception as e:
                        self.logger.warning(f"Error searching GitHub: {e}")

                # Fetch topic info for trending topics
                for topic in self.TOPICS[:5]:
                    try:
                        topic_url = f"{self.BASE_URL}/search/topics"
                        params = {'q': topic}

                        async with session.get(topic_url, headers={**headers, 'Accept': 'application/vnd.github.mercy-preview+json'}, params=params, timeout=10) as response:
                            if response.status == 200:
                                data = await response.json()
                                items = data.get('items', [])
                                if items:
                                    topic_data = items[0]
                                    trending_topics.append({
                                        'name': topic_data.get('name', ''),
                                        'display_name': topic_data.get('display_name', ''),
                                        'description': topic_data.get('short_description', ''),
                                        'created_by': topic_data.get('created_by', ''),
                                        'featured': topic_data.get('featured', False),
                                        'curated': topic_data.get('curated', False),
                                    })

                        await asyncio.sleep(0.5)

                    except Exception as e:
                        self.logger.warning(f"Error fetching topic {topic}: {e}")

            return {
                'repositories': all_repos,
                'topics': trending_topics,
                'source': 'github'
            }

        except Exception as e:
            self.logger.error(f"Error fetching GitHub data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process GitHub data into intelligence"""
        try:
            repos = raw_data.get('repositories', [])
            topics = raw_data.get('topics', [])

            # Analyze by language
            language_stats = {}
            for repo in repos:
                lang = repo.get('language', 'Unknown') or 'Unknown'
                if lang not in language_stats:
                    language_stats[lang] = {'count': 0, 'total_stars': 0}
                language_stats[lang]['count'] += 1
                language_stats[lang]['total_stars'] += repo.get('stars', 0)

            # Find most starred repos
            top_repos = sorted(repos, key=lambda x: x.get('stars', 0), reverse=True)[:10]

            # Extract common topics from repos
            all_topics = []
            for repo in repos:
                all_topics.extend(repo.get('topics', []))
            topic_frequency = {}
            for t in all_topics:
                topic_frequency[t] = topic_frequency.get(t, 0) + 1
            trending_repo_topics = sorted(topic_frequency.items(), key=lambda x: x[1], reverse=True)[:20]

            content = {
                'repositories': repos,
                'top_repos': top_repos,
                'topics': topics,
                'language_stats': language_stats,
                'trending_topics': trending_repo_topics,
                'total_repos': len(repos),
                'total_stars': sum(r.get('stars', 0) for r in repos),
            }

            quality_score = min(1.0, len(repos) / 30 + 0.3)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='github.com',
                data_type='developer_intelligence',
                content=content,
                metadata={
                    'repo_count': len(repos),
                    'languages': list(language_stats.keys()),
                    'source': 'github',
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['github', 'developer', 'open-source', 'trending', 'repos', 'ai', 'ml'],
                target_agents=['research_agent', 'trend_analysis_agent', 'competitor_analysis_agent'],
                target_advisors=['tech_advisor', 'developer_advocate', 'innovation_strategist']
            )

        except Exception as e:
            self.logger.error(f"Error processing GitHub data: {e}")
            return None

    def get_required_fields(self) -> List[str]:
        return ['name', 'stars']

    def get_relevance_keywords(self) -> List[str]:
        return ['github', 'repository', 'developer', 'open-source', 'trending', 'stars']

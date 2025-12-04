"""
NewsAPI Spider - Breaking News Intelligence
============================================

Session 343: Spider for NewsAPI.org to fetch breaking news.
Collects top headlines and everything news from 80k+ sources.

Uses NEWS_API_KEY from environment for authenticated requests.
"""

import aiohttp
import asyncio
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class NewsAPISpider(BaseIntelligenceSpider):
    """NewsAPI spider - breaking news from 80k+ sources worldwide"""

    BASE_URL = "https://newsapi.org/v2"

    # Categories to track
    CATEGORIES = [
        'technology',
        'business',
        'science',
        'entertainment',
        'health',
    ]

    # Countries for top headlines
    COUNTRIES = ['us', 'gb']

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)
        self.api_key = os.getenv('NEWS_API_KEY', '')

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch breaking news from NewsAPI"""
        if not self.api_key:
            self.logger.warning("NEWS_API_KEY not configured")
            return {'articles': [], 'source': 'newsapi', 'error': 'API key not configured'}

        try:
            all_articles = []

            async with aiohttp.ClientSession() as session:
                # Fetch top headlines by category
                for category in self.CATEGORIES[:3]:  # Limit to avoid rate limits
                    try:
                        url = f"{self.BASE_URL}/top-headlines"
                        params = {
                            'category': category,
                            'country': 'us',
                            'pageSize': 10,
                            'apiKey': self.api_key
                        }

                        async with session.get(url, params=params, timeout=15) as response:
                            if response.status == 200:
                                data = await response.json()
                                articles = data.get('articles', [])

                                for article in articles:
                                    all_articles.append({
                                        'title': article.get('title', ''),
                                        'description': article.get('description', ''),
                                        'url': article.get('url', ''),
                                        'source': article.get('source', {}).get('name', ''),
                                        'author': article.get('author', ''),
                                        'published_at': article.get('publishedAt', ''),
                                        'image_url': article.get('urlToImage', ''),
                                        'category': category,
                                        'data_source': 'newsapi',
                                        'type': 'news_article',
                                    })
                            else:
                                self.logger.warning(f"NewsAPI returned {response.status}")

                        await asyncio.sleep(0.3)

                    except Exception as e:
                        self.logger.warning(f"Error fetching {category} news: {e}")

                # Fetch technology news specifically (important for business research)
                try:
                    url = f"{self.BASE_URL}/everything"
                    params = {
                        'q': 'AI OR artificial intelligence OR startup OR technology',
                        'sortBy': 'publishedAt',
                        'pageSize': 20,
                        'language': 'en',
                        'apiKey': self.api_key
                    }

                    async with session.get(url, params=params, timeout=15) as response:
                        if response.status == 200:
                            data = await response.json()
                            articles = data.get('articles', [])

                            for article in articles:
                                article_data = {
                                    'title': article.get('title', ''),
                                    'description': article.get('description', ''),
                                    'url': article.get('url', ''),
                                    'source': article.get('source', {}).get('name', ''),
                                    'author': article.get('author', ''),
                                    'published_at': article.get('publishedAt', ''),
                                    'image_url': article.get('urlToImage', ''),
                                    'category': 'tech_search',
                                    'data_source': 'newsapi',
                                    'type': 'news_article',
                                }
                                # Avoid duplicates
                                if article_data['url'] not in [a['url'] for a in all_articles]:
                                    all_articles.append(article_data)

                except Exception as e:
                    self.logger.warning(f"Error fetching tech news: {e}")

            return {
                'articles': all_articles,
                'source': 'newsapi'
            }

        except Exception as e:
            self.logger.error(f"Error fetching NewsAPI data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process NewsAPI data into intelligence"""
        try:
            articles = raw_data.get('articles', [])

            # Categorize articles
            by_category = {}
            for article in articles:
                cat = article.get('category', 'general')
                if cat not in by_category:
                    by_category[cat] = []
                by_category[cat].append(article)

            # Extract sources
            sources = {}
            for article in articles:
                src = article.get('source', 'Unknown')
                sources[src] = sources.get(src, 0) + 1

            # Top sources
            top_sources = sorted(sources.items(), key=lambda x: x[1], reverse=True)[:10]

            content = {
                'articles': articles,
                'by_category': {k: len(v) for k, v in by_category.items()},
                'top_sources': top_sources,
                'total_articles': len(articles),
                'categories_covered': list(by_category.keys()),
            }

            quality_score = min(1.0, len(articles) / 40 + 0.3)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='newsapi.org',
                data_type='news_intelligence',
                content=content,
                metadata={
                    'article_count': len(articles),
                    'categories': list(by_category.keys()),
                    'source': 'newsapi',
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['news', 'headlines', 'breaking', 'technology', 'business', 'current_events'],
                target_agents=['research_agent', 'trend_analysis_agent', 'competitor_analysis_agent'],
                target_advisors=['news_analyst', 'market_strategist', 'business_advisor']
            )

        except Exception as e:
            self.logger.error(f"Error processing NewsAPI data: {e}")
            return None

    def get_required_fields(self) -> List[str]:
        return ['title', 'url']

    def get_relevance_keywords(self) -> List[str]:
        return ['news', 'headlines', 'breaking', 'current', 'latest', 'today']

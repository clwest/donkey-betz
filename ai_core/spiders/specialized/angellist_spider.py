"""
AngelList Spider - Startup Job & Investment Intelligence
=========================================================

Session 218: Specialized spider for AngelList/Wellfound startup ecosystem.
Focuses on startup jobs, funding rounds, and emerging companies.
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class AngelListSpider(BaseIntelligenceSpider):
    """AngelList/Wellfound spider - startup jobs and ecosystem intelligence"""

    # Wellfound (formerly AngelList Talent) doesn't have public RSS
    # We'll use tech startup job aggregators and news sources
    RSS_FEEDS = {
        'ycombinator': 'https://news.ycombinator.com/rss',
        'techstartups': 'https://techstartups.com/feed/',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.startup_stages = {
            'seed': ['seed', 'pre-seed', 'angel', 'bootstrapped'],
            'early': ['series a', 'series b', 'early stage', 'growth'],
            'growth': ['series c', 'series d', 'series e', 'late stage'],
            'public': ['ipo', 'public', 'nasdaq', 'nyse'],
        }

        self.role_types = {
            'engineering': ['engineer', 'developer', 'cto', 'technical', 'software'],
            'product': ['product manager', 'pm', 'product lead', 'product design'],
            'design': ['designer', 'ui', 'ux', 'creative', 'brand'],
            'growth': ['growth', 'marketing', 'sales', 'revenue', 'business development'],
            'operations': ['operations', 'ops', 'coo', 'finance', 'hr', 'people'],
            'founder': ['founder', 'ceo', 'co-founder', 'founding'],
        }

        self.industries = {
            'ai_ml': ['ai', 'machine learning', 'artificial intelligence', 'ml', 'deep learning'],
            'fintech': ['fintech', 'payments', 'banking', 'crypto', 'defi', 'blockchain'],
            'healthtech': ['healthtech', 'health', 'medical', 'biotech', 'healthcare'],
            'saas': ['saas', 'b2b', 'enterprise', 'software'],
            'ecommerce': ['ecommerce', 'e-commerce', 'marketplace', 'retail'],
            'edtech': ['edtech', 'education', 'learning', 'training'],
            'climate': ['climate', 'cleantech', 'sustainability', 'green'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch startup ecosystem data"""
        try:
            all_items = []

            for feed_name, feed_url in self.RSS_FEEDS.items():
                try:
                    feed = feedparser.parse(feed_url)
                    if feed.entries:
                        for entry in feed.entries[:25]:
                            item = {
                                'title': entry.get('title', ''),
                                'description': entry.get('summary', entry.get('description', ''))[:500],
                                'link': entry.get('link', ''),
                                'published': entry.get('published', ''),
                                'source': feed_name,
                            }
                            if item['title']:
                                all_items.append(item)
                except Exception as e:
                    self.logger.warning(f"Error fetching {feed_name} feed: {e}")

            return {'items': all_items, 'source': 'angellist_ecosystem'}

        except Exception as e:
            self.logger.error(f"Error fetching AngelList data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process startup ecosystem data"""
        try:
            items = raw_data.get('items', [])
            processed_items = []

            for item in items:
                processed = self._process_item(item)
                if processed:
                    processed_items.append(processed)

            # Filter for startup-relevant content
            startup_items = [i for i in processed_items if i.get('is_startup_relevant')]

            insights = self._generate_startup_insights(startup_items)

            content = {
                'items': startup_items,
                'insights': insights,
                'by_industry': self._group_by_industry(startup_items),
                'by_stage': self._group_by_stage(startup_items),
                'funding_signals': self._extract_funding_signals(startup_items),
                'hot_industries': self._identify_hot_industries(startup_items),
            }

            quality_score = min(1.0, len(startup_items) / 25 + 0.3)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='angel.co',
                data_type='startup_ecosystem',
                content=content,
                metadata={
                    'item_count': len(startup_items),
                    'source': 'angellist_ecosystem',
                    'feeds_scraped': list(self.RSS_FEEDS.keys()),
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['startups', 'jobs', 'funding', 'tech', 'venture'],
                target_agents=['startup_agent', 'job_agent', 'investment_agent'],
                target_advisors=['startup_advisor', 'venture_strategist']
            )

        except Exception as e:
            self.logger.error(f"Error processing AngelList data: {e}")
            return None

    def _process_item(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process individual item"""
        try:
            title = item.get('title', '')
            description = item.get('description', '')
            text = f"{title} {description}".lower()

            # Check if startup-relevant
            startup_keywords = ['startup', 'founder', 'funding', 'series', 'raise', 'venture', 'yc', 'ycombinator',
                              'launch', 'seed', 'angel', 'investor', 'equity', 'valuation', 'hiring']
            is_startup_relevant = any(kw in text for kw in startup_keywords)

            # Identify industry
            industry = 'general'
            for ind, keywords in self.industries.items():
                if any(kw in text for kw in keywords):
                    industry = ind
                    break

            # Identify stage
            stage = 'unknown'
            for stg, keywords in self.startup_stages.items():
                if any(kw in text for kw in keywords):
                    stage = stg
                    break

            # Check for funding news
            is_funding_news = any(word in text for word in ['raised', 'funding', 'series', 'million', 'billion', 'investment'])

            # Check for job posting
            is_job_related = any(word in text for word in ['hiring', 'job', 'role', 'position', 'join', 'team'])

            # Sentiment
            blob = TextBlob(f"{title} {description}")
            sentiment = blob.sentiment.polarity

            return {
                'title': title,
                'description': description[:300],
                'link': item.get('link', ''),
                'published': item.get('published', ''),
                'source': item.get('source', ''),
                'industry': industry,
                'stage': stage,
                'is_startup_relevant': is_startup_relevant,
                'is_funding_news': is_funding_news,
                'is_job_related': is_job_related,
                'sentiment': sentiment,
            }

        except Exception as e:
            self.logger.warning(f"Error processing item: {e}")
            return None

    def _generate_startup_insights(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate startup ecosystem insights"""
        if not items:
            return {}

        funding_news = [i for i in items if i.get('is_funding_news')]
        job_items = [i for i in items if i.get('is_job_related')]

        industry_counts = {}
        for item in items:
            ind = item.get('industry', 'general')
            industry_counts[ind] = industry_counts.get(ind, 0) + 1

        avg_sentiment = sum(i.get('sentiment', 0) for i in items) / len(items) if items else 0

        return {
            'total_items': len(items),
            'funding_news_count': len(funding_news),
            'job_related_count': len(job_items),
            'hot_industries': sorted(industry_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            'ecosystem_sentiment': 'bullish' if avg_sentiment > 0.1 else 'bearish' if avg_sentiment < -0.1 else 'neutral',
        }

    def _group_by_industry(self, items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group items by industry"""
        groups = {}
        for item in items:
            ind = item.get('industry', 'general')
            if ind not in groups:
                groups[ind] = []
            groups[ind].append({'title': item.get('title'), 'link': item.get('link')})
        return groups

    def _group_by_stage(self, items: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count items by startup stage"""
        counts = {}
        for item in items:
            stage = item.get('stage', 'unknown')
            counts[stage] = counts.get(stage, 0) + 1
        return counts

    def _extract_funding_signals(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract funding-related news"""
        funding = []
        for item in items:
            if item.get('is_funding_news'):
                funding.append({
                    'title': item.get('title'),
                    'industry': item.get('industry'),
                    'stage': item.get('stage'),
                    'link': item.get('link'),
                })
        return funding[:10]

    def _identify_hot_industries(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify hot industries based on activity"""
        industry_data = {}
        for item in items:
            ind = item.get('industry', 'general')
            if ind not in industry_data:
                industry_data[ind] = {'count': 0, 'funding_news': 0, 'sentiment_sum': 0}
            industry_data[ind]['count'] += 1
            if item.get('is_funding_news'):
                industry_data[ind]['funding_news'] += 1
            industry_data[ind]['sentiment_sum'] += item.get('sentiment', 0)

        results = []
        for ind, data in industry_data.items():
            avg_sentiment = data['sentiment_sum'] / data['count'] if data['count'] > 0 else 0
            results.append({
                'industry': ind,
                'activity_count': data['count'],
                'funding_news': data['funding_news'],
                'sentiment': round(avg_sentiment, 2),
            })

        return sorted(results, key=lambda x: x['activity_count'], reverse=True)[:5]

    def get_required_fields(self) -> List[str]:
        return ['title']

    def get_relevance_keywords(self) -> List[str]:
        return ['startup', 'funding', 'venture', 'founder', 'series', 'angel']

"""
The Verge Spider - Consumer Tech & Culture News Intelligence
===========================================================

Session 218: Specialized spider for The Verge news coverage.
Focuses on consumer tech, gadgets, apps, and tech culture.
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class TheVergeSpider(BaseIntelligenceSpider):
    """The Verge tech news spider - consumer tech, reviews, and culture"""

    # RSS Feed URLs for The Verge sections
    RSS_FEEDS = {
        'all': 'https://www.theverge.com/rss/index.xml',
        'tech': 'https://www.theverge.com/tech/rss/index.xml',
        'reviews': 'https://www.theverge.com/reviews/rss/index.xml',
        'science': 'https://www.theverge.com/science/rss/index.xml',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.content_types = {
            'review': ['review', 'hands-on', 'first look', 'tested', 'verdict'],
            'news': ['announces', 'launches', 'reveals', 'reportedly', 'confirms'],
            'analysis': ['why', 'how', 'what this means', 'explained', 'deep dive'],
            'rumor': ['rumor', 'leak', 'reportedly', 'might', 'could', 'expected'],
        }

        self.product_categories = {
            'smartphones': ['iphone', 'android', 'pixel', 'galaxy', 'smartphone', 'phone'],
            'computers': ['macbook', 'laptop', 'pc', 'desktop', 'chromebook', 'tablet', 'ipad'],
            'wearables': ['watch', 'airpods', 'earbuds', 'headphones', 'fitbit', 'wearable'],
            'gaming': ['playstation', 'xbox', 'nintendo', 'switch', 'game', 'gaming', 'steam'],
            'smart_home': ['smart home', 'alexa', 'google home', 'nest', 'ring', 'thermostat'],
            'ev': ['tesla', 'ev', 'electric vehicle', 'rivian', 'charging', 'lucid'],
            'ai_tools': ['chatgpt', 'ai', 'copilot', 'gemini', 'claude', 'midjourney', 'dall-e'],
            'streaming': ['netflix', 'disney+', 'hbo', 'streaming', 'spotify', 'youtube'],
        }

        self.companies = {
            'apple': ['apple', 'iphone', 'mac', 'ipad', 'airpods', 'wwdc'],
            'google': ['google', 'android', 'pixel', 'chrome', 'youtube', 'gemini'],
            'microsoft': ['microsoft', 'windows', 'xbox', 'surface', 'copilot', 'office'],
            'meta': ['meta', 'facebook', 'instagram', 'whatsapp', 'quest', 'threads'],
            'amazon': ['amazon', 'alexa', 'echo', 'kindle', 'fire', 'prime'],
            'openai': ['openai', 'chatgpt', 'gpt-4', 'dall-e', 'sora'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch RSS feeds from The Verge"""
        try:
            all_articles = []

            for feed_name, feed_url in self.RSS_FEEDS.items():
                try:
                    feed = feedparser.parse(feed_url)
                    if feed.entries:
                        for entry in feed.entries[:15]:
                            # Extract content from various possible fields
                            content = ''
                            if hasattr(entry, 'content') and entry.content:
                                content = entry.content[0].get('value', '')
                            elif hasattr(entry, 'summary'):
                                content = entry.summary

                            article = {
                                'title': entry.get('title', ''),
                                'summary': content[:500] if content else '',
                                'link': entry.get('link', ''),
                                'published': entry.get('published', ''),
                                'author': entry.get('author', 'The Verge'),
                                'tags': [tag.term for tag in entry.get('tags', [])] if hasattr(entry, 'tags') else [],
                                'feed_source': feed_name,
                            }
                            if article['title']:
                                all_articles.append(article)
                except Exception as e:
                    self.logger.warning(f"Error fetching {feed_name} feed: {e}")

            return {'articles': all_articles, 'source': 'theverge'}

        except Exception as e:
            self.logger.error(f"Error fetching The Verge data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process The Verge articles"""
        try:
            articles = raw_data.get('articles', [])
            processed_articles = []

            for article in articles:
                processed = self._process_article(article)
                if processed:
                    processed_articles.append(processed)

            # Generate consumer tech insights
            insights = self._generate_consumer_tech_insights(processed_articles)

            content = {
                'articles': processed_articles,
                'insights': insights,
                'product_coverage': self._analyze_product_coverage(processed_articles),
                'company_mentions': self._analyze_company_mentions(processed_articles),
                'reviews': self._extract_reviews(processed_articles),
                'trending_topics': self._extract_trending(processed_articles),
            }

            quality_score = min(1.0, len(processed_articles) / 30 + 0.3)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='theverge.com',
                data_type='consumer_tech_news',
                content=content,
                metadata={
                    'article_count': len(processed_articles),
                    'source': 'theverge',
                    'feeds_scraped': list(self.RSS_FEEDS.keys()),
                    'review_count': len([a for a in processed_articles if a.get('content_type') == 'review']),
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['consumer_tech', 'gadgets', 'reviews', 'apps', 'news'],
                target_agents=['research_agent', 'trend_analysis_agent', 'product_agent'],
                target_advisors=['product_strategist', 'consumer_analyst']
            )

        except Exception as e:
            self.logger.error(f"Error processing The Verge data: {e}")
            return None

    def _process_article(self, article: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process individual article"""
        try:
            title = article.get('title', '')
            summary = article.get('summary', '')
            text = f"{title} {summary}".lower()

            # Sentiment analysis
            blob = TextBlob(f"{title} {summary}")
            sentiment = {
                'polarity': blob.sentiment.polarity,
                'subjectivity': blob.sentiment.subjectivity,
                'tone': 'positive' if blob.sentiment.polarity > 0.15 else 'negative' if blob.sentiment.polarity < -0.15 else 'neutral'
            }

            # Determine content type
            content_type = 'news'
            for ctype, keywords in self.content_types.items():
                if any(kw in text for kw in keywords):
                    content_type = ctype
                    break

            # Identify product categories
            product_cats = []
            for cat, keywords in self.product_categories.items():
                if any(kw in text for kw in keywords):
                    product_cats.append(cat)

            # Identify companies mentioned
            companies_mentioned = []
            for company, keywords in self.companies.items():
                if any(kw in text for kw in keywords):
                    companies_mentioned.append(company)

            # Check if it's a review (important for Verge)
            is_review = content_type == 'review' or 'review' in text or 'reviews' in article.get('feed_source', '')

            # Extract score if it's a review (simplified)
            review_score = self._extract_review_score(title, summary) if is_review else None

            return {
                'title': title,
                'summary': summary[:400] if summary else '',
                'link': article.get('link', ''),
                'published': article.get('published', ''),
                'author': article.get('author', ''),
                'sentiment': sentiment,
                'content_type': content_type,
                'product_categories': product_cats or ['general'],
                'companies_mentioned': companies_mentioned,
                'is_review': is_review,
                'review_score': review_score,
                'tags': article.get('tags', []),
            }

        except Exception as e:
            self.logger.warning(f"Error processing article: {e}")
            return None

    def _extract_review_score(self, title: str, summary: str) -> Optional[str]:
        """Extract review score if present"""
        import re

        text = f"{title} {summary}"

        # Common score patterns
        patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:out of|/)\s*10',
            r'score[:\s]+(\d+(?:\.\d+)?)',
            r'rating[:\s]+(\d+(?:\.\d+)?)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return f"{match.group(1)}/10"

        return None

    def _generate_consumer_tech_insights(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate consumer tech insights"""
        if not articles:
            return {}

        reviews = [a for a in articles if a.get('is_review')]
        news = [a for a in articles if a.get('content_type') == 'news']

        # Find hot products
        product_mentions = {}
        for article in articles:
            for cat in article.get('product_categories', []):
                product_mentions[cat] = product_mentions.get(cat, 0) + 1

        hot_products = sorted(product_mentions.items(), key=lambda x: x[1], reverse=True)[:3]

        return {
            'total_coverage': len(articles),
            'review_count': len(reviews),
            'news_count': len(news),
            'hot_products': [p[0] for p in hot_products],
            'most_covered_company': self._get_most_mentioned_company(articles),
            'overall_sentiment': self._calculate_overall_sentiment(articles),
        }

    def _get_most_mentioned_company(self, articles: List[Dict[str, Any]]) -> str:
        """Get most mentioned company"""
        company_counts = {}
        for article in articles:
            for company in article.get('companies_mentioned', []):
                company_counts[company] = company_counts.get(company, 0) + 1

        if company_counts:
            return max(company_counts.items(), key=lambda x: x[1])[0]
        return 'various'

    def _calculate_overall_sentiment(self, articles: List[Dict[str, Any]]) -> str:
        """Calculate overall sentiment"""
        if not articles:
            return 'neutral'

        avg_polarity = sum(a.get('sentiment', {}).get('polarity', 0) for a in articles) / len(articles)

        if avg_polarity > 0.1:
            return 'positive'
        elif avg_polarity < -0.1:
            return 'negative'
        return 'neutral'

    def _analyze_product_coverage(self, articles: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Analyze coverage by product category"""
        coverage = {}

        for article in articles:
            for cat in article.get('product_categories', ['general']):
                if cat not in coverage:
                    coverage[cat] = {'count': 0, 'sentiment_sum': 0, 'reviews': 0}
                coverage[cat]['count'] += 1
                coverage[cat]['sentiment_sum'] += article.get('sentiment', {}).get('polarity', 0)
                if article.get('is_review'):
                    coverage[cat]['reviews'] += 1

        # Calculate averages
        for cat in coverage:
            if coverage[cat]['count'] > 0:
                coverage[cat]['avg_sentiment'] = round(coverage[cat]['sentiment_sum'] / coverage[cat]['count'], 2)
            del coverage[cat]['sentiment_sum']

        return coverage

    def _analyze_company_mentions(self, articles: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Analyze company mentions"""
        mentions = {}

        for article in articles:
            for company in article.get('companies_mentioned', []):
                if company not in mentions:
                    mentions[company] = {'count': 0, 'sentiment_sum': 0, 'articles': []}
                mentions[company]['count'] += 1
                mentions[company]['sentiment_sum'] += article.get('sentiment', {}).get('polarity', 0)
                if len(mentions[company]['articles']) < 3:
                    mentions[company]['articles'].append(article.get('title'))

        # Calculate averages
        for company in mentions:
            if mentions[company]['count'] > 0:
                mentions[company]['avg_sentiment'] = round(mentions[company]['sentiment_sum'] / mentions[company]['count'], 2)
            del mentions[company]['sentiment_sum']

        return mentions

    def _extract_reviews(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract review articles"""
        reviews = []
        for article in articles:
            if article.get('is_review'):
                reviews.append({
                    'title': article.get('title'),
                    'product_categories': article.get('product_categories'),
                    'sentiment': article.get('sentiment', {}).get('tone'),
                    'score': article.get('review_score'),
                    'link': article.get('link'),
                })
        return reviews[:10]

    def _extract_trending(self, articles: List[Dict[str, Any]]) -> List[str]:
        """Extract trending topics"""
        all_tags = []
        for article in articles:
            all_tags.extend(article.get('tags', []))
            all_tags.extend(article.get('product_categories', []))

        # Count frequencies
        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        return [t[0] for t in sorted_tags[:10]]

    def get_required_fields(self) -> List[str]:
        return ['title']

    def get_relevance_keywords(self) -> List[str]:
        return ['tech', 'review', 'gadget', 'app', 'iphone', 'android', 'gaming']

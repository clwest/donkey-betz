"""
TechCrunch Spider - Tech Startup & AI News Intelligence
=======================================================

Session 218: Specialized spider for TechCrunch news coverage.
Focuses on startups, AI, funding, and tech industry trends.
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class TechCrunchSpider(BaseIntelligenceSpider):
    """TechCrunch tech news spider - startups, AI, and funding news"""

    # RSS Feed URLs for different TechCrunch sections
    RSS_FEEDS = {
        'main': 'https://techcrunch.com/feed/',
        'startups': 'https://techcrunch.com/category/startups/feed/',
        'ai': 'https://techcrunch.com/category/artificial-intelligence/feed/',
        'venture': 'https://techcrunch.com/category/venture/feed/',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        # Session 495: Added defense_tech, healthtech, cybersecurity categories
        self.tech_categories = {
            'ai_ml': ['ai', 'artificial intelligence', 'machine learning', 'gpt', 'llm', 'neural', 'deep learning', 'generative ai', 'transformer'],
            'startups': ['startup', 'founded', 'launch', 'seed', 'series a', 'series b', 'funding', 'unicorn', 'valuation'],
            'big_tech': ['google', 'apple', 'microsoft', 'amazon', 'meta', 'facebook', 'openai', 'anthropic'],
            'crypto_web3': ['crypto', 'blockchain', 'web3', 'nft', 'defi', 'bitcoin', 'ethereum'],
            'fintech': ['fintech', 'payments', 'banking', 'lending', 'insurtech', 'neobank'],
            'saas': ['saas', 'enterprise', 'b2b', 'software', 'cloud'],
            'hardware': ['hardware', 'chip', 'semiconductor', 'device', 'gadget', 'robotics'],
            'defense_tech': ['defense', 'military', 'dod', 'pentagon', 'government contract', 'aerospace', 'defense tech'],
            'healthtech': ['healthtech', 'biotech', 'medtech', 'digital health', 'telehealth', 'fda', 'clinical trial'],
            'cybersecurity': ['cybersecurity', 'infosec', 'security startup', 'breach', 'ransomware', 'vulnerability', 'ciso'],
            'climate': ['climate', 'cleantech', 'sustainability', 'carbon', 'green tech', 'renewable'],
        }

        self.funding_keywords = {
            'seed': ['seed', 'pre-seed', 'angel'],
            'series_a': ['series a', '$5m', '$10m', '$15m'],
            'series_b': ['series b', '$20m', '$30m', '$50m'],
            'series_c_plus': ['series c', 'series d', 'series e', '$100m', '$200m'],
            'ipo': ['ipo', 'public offering', 'going public'],
            'acquisition': ['acquired', 'acquisition', 'buys', 'purchased'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch RSS feeds from TechCrunch"""
        try:
            all_articles = []

            for feed_name, feed_url in self.RSS_FEEDS.items():
                try:
                    feed = feedparser.parse(feed_url)
                    if feed.entries:
                        for entry in feed.entries[:15]:  # Limit per feed
                            article = {
                                'title': entry.get('title', ''),
                                'summary': entry.get('summary', ''),
                                'link': entry.get('link', ''),
                                'published': entry.get('published', ''),
                                'author': entry.get('author', 'TechCrunch'),
                                'tags': [tag.term for tag in entry.get('tags', [])],
                                'feed_source': feed_name,
                            }
                            if article['title']:
                                all_articles.append(article)
                except Exception as e:
                    self.logger.warning(f"Error fetching {feed_name} feed: {e}")

            return {'articles': all_articles, 'source': 'techcrunch'}

        except Exception as e:
            self.logger.error(f"Error fetching TechCrunch data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process TechCrunch articles"""
        try:
            articles = raw_data.get('articles', [])
            processed_articles = []

            for article in articles:
                processed = self._process_article(article)
                if processed:
                    processed_articles.append(processed)

            # Generate analytics
            analytics = self._generate_analytics(processed_articles)

            content = {
                'articles': processed_articles,
                'analytics': analytics,
                'trending_topics': self._extract_trending_topics(processed_articles),
                'funding_roundup': self._extract_funding_news(processed_articles),
                'ai_highlights': self._extract_ai_news(processed_articles),
            }

            quality_score = min(1.0, len(processed_articles) / 30 + 0.3)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='techcrunch.com',
                data_type='tech_news',
                content=content,
                metadata={
                    'article_count': len(processed_articles),
                    'source': 'techcrunch',
                    'feeds_scraped': list(self.RSS_FEEDS.keys()),
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['tech', 'startups', 'ai', 'funding', 'news'],
                target_agents=['research_agent', 'trend_analysis_agent', 'content_agent'],
                target_advisors=['tech_strategist', 'venture_analyst']
            )

        except Exception as e:
            self.logger.error(f"Error processing TechCrunch data: {e}")
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
                'classification': 'positive' if blob.sentiment.polarity > 0.1 else 'negative' if blob.sentiment.polarity < -0.1 else 'neutral'
            }

            # Categorize
            categories = []
            for cat, keywords in self.tech_categories.items():
                if any(kw in text for kw in keywords):
                    categories.append(cat)

            # Check for funding news
            funding_stage = None
            for stage, keywords in self.funding_keywords.items():
                if any(kw in text for kw in keywords):
                    funding_stage = stage
                    break

            # Extract mentioned companies (simple heuristic)
            companies = self._extract_companies(title, summary)

            return {
                'title': title,
                'summary': summary[:500] if summary else '',
                'link': article.get('link', ''),
                'published': article.get('published', ''),
                'author': article.get('author', ''),
                'sentiment': sentiment,
                'categories': categories or ['general'],
                'funding_stage': funding_stage,
                'companies_mentioned': companies,
                'tags': article.get('tags', []),
                'is_ai_related': 'ai_ml' in categories,
                'is_funding_news': funding_stage is not None,
            }

        except Exception as e:
            self.logger.warning(f"Error processing article: {e}")
            return None

    def _extract_companies(self, title: str, summary: str) -> List[str]:
        """Extract company names from text"""
        import re
        companies = []

        # Common patterns for company names
        patterns = [
            r'\b([A-Z][a-z]+(?:AI|Labs?|Tech|\.io|\.ai)?)\b',
        ]

        text = f"{title} {summary}"
        for pattern in patterns:
            matches = re.findall(pattern, text)
            companies.extend(matches)

        # Filter out common words
        common_words = {'The', 'This', 'That', 'With', 'From', 'Into', 'About', 'After', 'Before', 'While'}
        companies = [c for c in companies if c not in common_words]

        return list(set(companies))[:5]

    def _generate_analytics(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate analytics from articles"""
        total = len(articles)
        if total == 0:
            return {}

        return {
            'total_articles': total,
            'sentiment_breakdown': {
                'positive': sum(1 for a in articles if a.get('sentiment', {}).get('classification') == 'positive'),
                'negative': sum(1 for a in articles if a.get('sentiment', {}).get('classification') == 'negative'),
                'neutral': sum(1 for a in articles if a.get('sentiment', {}).get('classification') == 'neutral'),
            },
            'category_distribution': self._count_categories(articles),
            'ai_article_count': sum(1 for a in articles if a.get('is_ai_related')),
            'funding_news_count': sum(1 for a in articles if a.get('is_funding_news')),
        }

    def _count_categories(self, articles: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count articles per category"""
        counts = {}
        for article in articles:
            for cat in article.get('categories', []):
                counts[cat] = counts.get(cat, 0) + 1
        return counts

    def _extract_trending_topics(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract trending topics"""
        topic_counts = {}

        for article in articles:
            for cat in article.get('categories', []):
                topic_counts[cat] = topic_counts.get(cat, 0) + 1
            for tag in article.get('tags', []):
                topic_counts[tag] = topic_counts.get(tag, 0) + 1

        sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
        return [{'topic': t, 'count': c} for t, c in sorted_topics[:10]]

    def _extract_funding_news(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract funding-related news"""
        funding_news = []
        for article in articles:
            if article.get('is_funding_news'):
                funding_news.append({
                    'title': article.get('title'),
                    'stage': article.get('funding_stage'),
                    'companies': article.get('companies_mentioned', []),
                    'link': article.get('link'),
                })
        return funding_news[:10]

    def _extract_ai_news(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract AI-related news"""
        ai_news = []
        for article in articles:
            if article.get('is_ai_related'):
                ai_news.append({
                    'title': article.get('title'),
                    'summary': article.get('summary', '')[:200],
                    'sentiment': article.get('sentiment', {}).get('classification'),
                    'link': article.get('link'),
                })
        return ai_news[:10]

    def get_required_fields(self) -> List[str]:
        return ['title']

    def get_relevance_keywords(self) -> List[str]:
        return ['startup', 'ai', 'funding', 'tech', 'venture', 'series']

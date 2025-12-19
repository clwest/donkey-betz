"""
Crunchbase News Spider - Startup Funding Intelligence
======================================================

Session 495: Added for comprehensive startup/VC funding coverage.
THE gold standard for startup funding data - rounds, valuations, unicorns, M&A.
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
import re
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class CrunchbaseSpider(BaseIntelligenceSpider):
    """Crunchbase News spider - startup funding, valuations, and M&A intelligence"""

    RSS_FEEDS = {
        'main': 'https://news.crunchbase.com/feed/',
        'venture': 'https://news.crunchbase.com/venture/feed/',
        'startups': 'https://news.crunchbase.com/startups/feed/',
        'ma': 'https://news.crunchbase.com/ma/feed/',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        # Funding stage detection
        self.funding_patterns = {
            'pre_seed': [r'pre-seed', r'pre seed', r'\$\d+k', r'\$[1-4]m\b'],
            'seed': [r'\bseed\b', r'seed round', r'\$[1-5]m\b'],
            'series_a': [r'series a', r'\$[5-9]m\b', r'\$1[0-5]m\b'],
            'series_b': [r'series b', r'\$[2-5]0m\b', r'\$[6-9]0m\b'],
            'series_c': [r'series c', r'\$1[0-5]0m\b'],
            'series_d_plus': [r'series [d-z]', r'\$[2-9][0-9]0m\b', r'\$\d+b\b'],
            'ipo': [r'\bipo\b', r'goes public', r'public offering', r'nasdaq', r'nyse'],
            'acquisition': [r'acquires', r'acquired', r'acquisition', r'buys', r'merger'],
            'unicorn': [r'unicorn', r'\$1b valuation', r'billion.dollar'],
        }

        # Sector categories
        self.sectors = {
            'ai_ml': ['ai', 'artificial intelligence', 'machine learning', 'llm', 'generative ai', 'gpt', 'anthropic', 'openai'],
            'fintech': ['fintech', 'payments', 'banking', 'neobank', 'lending', 'insurtech', 'crypto'],
            'healthtech': ['healthtech', 'biotech', 'medtech', 'digital health', 'telehealth', 'clinical'],
            'defense_tech': ['defense', 'military', 'government', 'aerospace', 'security', 'defense tech'],
            'cybersecurity': ['cybersecurity', 'security startup', 'infosec', 'cyber'],
            'saas': ['saas', 'enterprise', 'b2b', 'software', 'cloud'],
            'ecommerce': ['ecommerce', 'e-commerce', 'retail tech', 'marketplace'],
            'climate': ['climate', 'cleantech', 'sustainability', 'green', 'carbon'],
            'robotics': ['robotics', 'automation', 'autonomous', 'drones'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch RSS feeds from Crunchbase News"""
        try:
            all_articles = []

            for feed_name, feed_url in self.RSS_FEEDS.items():
                try:
                    feed = feedparser.parse(feed_url)
                    if feed.entries:
                        for entry in feed.entries[:20]:
                            article = {
                                'title': entry.get('title', ''),
                                'summary': entry.get('summary', entry.get('description', '')),
                                'link': entry.get('link', ''),
                                'published': entry.get('published', ''),
                                'author': entry.get('author', 'Crunchbase News'),
                                'tags': [tag.term for tag in entry.get('tags', [])],
                                'feed_source': feed_name,
                            }
                            if article['title']:
                                all_articles.append(article)
                except Exception as e:
                    self.logger.warning(f"Error fetching {feed_name} feed: {e}")

            return {'articles': all_articles, 'source': 'crunchbase'}

        except Exception as e:
            self.logger.error(f"Error fetching Crunchbase data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process Crunchbase articles with funding intelligence"""
        try:
            articles = raw_data.get('articles', [])
            processed_articles = []

            for article in articles:
                processed = self._process_article(article)
                if processed:
                    processed_articles.append(processed)

            # Generate funding-focused analytics
            analytics = self._generate_funding_analytics(processed_articles)

            content = {
                'articles': processed_articles,
                'analytics': analytics,
                'funding_rounds': self._extract_funding_rounds(processed_articles),
                'unicorn_news': [a for a in processed_articles if a.get('is_unicorn_news')],
                'ma_activity': [a for a in processed_articles if a.get('funding_stage') == 'acquisition'],
                'sector_breakdown': self._get_sector_breakdown(processed_articles),
            }

            quality_score = min(1.0, len(processed_articles) / 40 + 0.4)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='news.crunchbase.com',
                data_type='startup_funding',
                content=content,
                metadata={
                    'article_count': len(processed_articles),
                    'source': 'crunchbase',
                    'feeds_scraped': list(self.RSS_FEEDS.keys()),
                    'funding_articles': sum(1 for a in processed_articles if a.get('funding_stage')),
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['startups', 'funding', 'venture capital', 'unicorns', 'M&A', 'valuations'],
                target_agents=['research_agent', 'trend_analysis_agent', 'opportunity_scoring_agent'],
                target_advisors=['venture_analyst', 'startup_strategist']
            )

        except Exception as e:
            self.logger.error(f"Error processing Crunchbase data: {e}")
            return None

    def _process_article(self, article: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process individual article with funding extraction"""
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

            # Detect funding stage
            funding_stage = self._detect_funding_stage(text)

            # Detect sectors
            sectors = self._detect_sectors(text)

            # Extract funding amount
            funding_amount = self._extract_funding_amount(text)

            # Extract company names
            companies = self._extract_companies(title, summary)

            # Check for unicorn news
            is_unicorn = any(term in text for term in ['unicorn', '$1b', 'billion dollar', 'billion-dollar'])

            return {
                'title': title,
                'summary': summary[:500] if summary else '',
                'link': article.get('link', ''),
                'published': article.get('published', ''),
                'author': article.get('author', ''),
                'sentiment': sentiment,
                'funding_stage': funding_stage,
                'funding_amount': funding_amount,
                'sectors': sectors,
                'companies_mentioned': companies,
                'tags': article.get('tags', []),
                'is_unicorn_news': is_unicorn,
                'is_funding_news': funding_stage is not None,
                'feed_source': article.get('feed_source', 'main'),
            }

        except Exception as e:
            self.logger.warning(f"Error processing article: {e}")
            return None

    def _detect_funding_stage(self, text: str) -> Optional[str]:
        """Detect funding stage from text"""
        for stage, patterns in self.funding_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return stage
        return None

    def _detect_sectors(self, text: str) -> List[str]:
        """Detect sectors from text"""
        detected = []
        for sector, keywords in self.sectors.items():
            if any(kw in text for kw in keywords):
                detected.append(sector)
        return detected or ['general']

    def _extract_funding_amount(self, text: str) -> Optional[str]:
        """Extract funding amount from text"""
        # Match patterns like $50M, $1.5B, $100 million, etc.
        patterns = [
            r'\$(\d+(?:\.\d+)?)\s*(?:billion|b)\b',
            r'\$(\d+(?:\.\d+)?)\s*(?:million|m)\b',
            r'\$(\d+(?:\.\d+)?)[mb]\b',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        return None

    def _extract_companies(self, title: str, summary: str) -> List[str]:
        """Extract company names from text"""
        companies = []
        # Look for capitalized words that might be company names
        text = f"{title} {summary}"
        # Match CamelCase or single capitalized words followed by common suffixes
        pattern = r'\b([A-Z][a-z]+(?:[A-Z][a-z]+)*(?:\.(?:ai|io|co|ly))?)\b'
        matches = re.findall(pattern, text)

        # Filter out common words
        common_words = {'The', 'This', 'That', 'With', 'From', 'Into', 'About', 'After',
                       'Before', 'While', 'When', 'What', 'Which', 'Where', 'Series',
                       'Funding', 'Round', 'Million', 'Billion', 'Raises', 'Secures'}
        companies = [c for c in matches if c not in common_words]

        return list(set(companies))[:5]

    def _generate_funding_analytics(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate funding-focused analytics"""
        total = len(articles)
        if total == 0:
            return {}

        funding_articles = [a for a in articles if a.get('is_funding_news')]

        return {
            'total_articles': total,
            'funding_news_count': len(funding_articles),
            'unicorn_mentions': sum(1 for a in articles if a.get('is_unicorn_news')),
            'stage_distribution': self._count_stages(articles),
            'sector_distribution': self._count_sectors(articles),
            'sentiment_breakdown': {
                'positive': sum(1 for a in articles if a.get('sentiment', {}).get('classification') == 'positive'),
                'negative': sum(1 for a in articles if a.get('sentiment', {}).get('classification') == 'negative'),
                'neutral': sum(1 for a in articles if a.get('sentiment', {}).get('classification') == 'neutral'),
            },
        }

    def _count_stages(self, articles: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count articles per funding stage"""
        counts = {}
        for article in articles:
            stage = article.get('funding_stage')
            if stage:
                counts[stage] = counts.get(stage, 0) + 1
        return counts

    def _count_sectors(self, articles: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count articles per sector"""
        counts = {}
        for article in articles:
            for sector in article.get('sectors', []):
                counts[sector] = counts.get(sector, 0) + 1
        return counts

    def _extract_funding_rounds(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract funding round details"""
        rounds = []
        for article in articles:
            if article.get('is_funding_news'):
                rounds.append({
                    'title': article.get('title'),
                    'stage': article.get('funding_stage'),
                    'amount': article.get('funding_amount'),
                    'companies': article.get('companies_mentioned', []),
                    'sectors': article.get('sectors', []),
                    'link': article.get('link'),
                })
        return rounds[:15]

    def _get_sector_breakdown(self, articles: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group articles by sector"""
        breakdown = {}
        for article in articles:
            for sector in article.get('sectors', ['general']):
                if sector not in breakdown:
                    breakdown[sector] = []
                if len(breakdown[sector]) < 5:
                    breakdown[sector].append({
                        'title': article.get('title'),
                        'link': article.get('link'),
                        'funding_stage': article.get('funding_stage'),
                    })
        return breakdown

    def get_required_fields(self) -> List[str]:
        return ['title']

    def get_relevance_keywords(self) -> List[str]:
        return ['startup', 'funding', 'raises', 'series', 'valuation', 'unicorn', 'acquisition', 'venture']

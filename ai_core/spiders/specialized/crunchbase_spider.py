"""
Crunchbase News Spider - Startup Funding Intelligence
======================================================

Session 534: Simplified to work with spider network interface.
Crunchbase News provides startup/funding coverage via RSS feeds.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class CrunchbaseSpider:
    """Crunchbase News spider - startup funding and M&A intelligence via RSS"""

    name = "crunchbase"

    RSS_FEEDS = {
        'main': 'https://news.crunchbase.com/feed/',
        'venture': 'https://news.crunchbase.com/venture/feed/',
        'startups': 'https://news.crunchbase.com/startups/feed/',
        'ma': 'https://news.crunchbase.com/ma/feed/',
    }

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch news articles from Crunchbase News RSS feeds.

        Args:
            max_results: Maximum number of articles to fetch

        Returns:
            List of article dictionaries
        """
        all_articles = []
        seen_urls = set()

        for feed_name, feed_url in self.RSS_FEEDS.items():
            try:
                feed = feedparser.parse(feed_url)

                for entry in feed.entries[:20]:
                    url = entry.get('link', '')

                    # Skip duplicates
                    if url in seen_urls:
                        continue
                    seen_urls.add(url)

                    title = entry.get('title', '')
                    if not title:
                        continue

                    summary = entry.get('summary', entry.get('description', ''))
                    # Clean HTML from summary
                    if summary:
                        summary = re.sub(r'<[^>]+>', '', summary)[:500]

                    text = f"{title} {summary}".lower()

                    # Extract funding info
                    funding_stage = self._detect_funding_stage(text)
                    funding_amount = self._extract_funding_amount(text)
                    sector = self._detect_sector(text)

                    article = {
                        'title': title,
                        'url': url,
                        'summary': summary,
                        'description': summary,
                        'published': entry.get('published', ''),
                        'author': entry.get('author', 'Crunchbase News'),
                        'category': feed_name,
                        'source': 'Crunchbase News',
                        'data_type': 'funding_news',
                        'funding_stage': funding_stage,
                        'funding_amount': funding_amount,
                        'sector': sector,
                        'tags': ['startups', 'funding', 'venture', feed_name],
                        'timestamp': datetime.now().isoformat(),
                    }
                    all_articles.append(article)

                    if len(all_articles) >= max_results:
                        break

            except Exception as e:
                logger.warning(f"Error fetching Crunchbase {feed_name} feed: {e}")
                continue

            if len(all_articles) >= max_results:
                break

        # If RSS feeds are blocked/empty, return curated topics
        if len(all_articles) == 0:
            all_articles = self._get_curated_topics()

        logger.info(f"Crunchbase spider collected {len(all_articles)} articles")
        return all_articles[:max_results]

    def _detect_funding_stage(self, text: str) -> Optional[str]:
        """Detect funding stage from text."""
        stages = {
            'pre_seed': ['pre-seed', 'pre seed'],
            'seed': [' seed ', 'seed round', 'seed funding'],
            'series_a': ['series a'],
            'series_b': ['series b'],
            'series_c': ['series c'],
            'series_d_plus': ['series d', 'series e', 'series f'],
            'ipo': ['ipo', 'goes public', 'public offering'],
            'acquisition': ['acquires', 'acquired', 'acquisition', 'buys', 'merger'],
        }

        for stage, keywords in stages.items():
            if any(kw in text for kw in keywords):
                return stage
        return None

    def _extract_funding_amount(self, text: str) -> Optional[str]:
        """Extract funding amount from text."""
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

    def _detect_sector(self, text: str) -> str:
        """Detect sector from text."""
        sectors = {
            'ai_ml': ['ai', 'artificial intelligence', 'machine learning', 'llm', 'generative'],
            'fintech': ['fintech', 'payments', 'banking', 'neobank', 'crypto'],
            'healthtech': ['healthtech', 'biotech', 'medtech', 'digital health'],
            'cybersecurity': ['cybersecurity', 'security startup', 'infosec'],
            'saas': ['saas', 'enterprise', 'b2b', 'software'],
            'climate': ['climate', 'cleantech', 'sustainability', 'green'],
            'defense': ['defense', 'military', 'government', 'aerospace'],
        }

        for sector, keywords in sectors.items():
            if any(kw in text for kw in keywords):
                return sector
        return 'general'

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated funding topics when RSS fails."""
        topics = [
            ('AI Startup Funding Trends', 'ai_ml', 'Latest funding rounds in AI, ML, and generative AI startups.'),
            ('Fintech Investment Activity', 'fintech', 'Banking, payments, and crypto startup funding news.'),
            ('Healthtech Funding Rounds', 'healthtech', 'Digital health, biotech, and medtech investment activity.'),
            ('Cybersecurity Startup Funding', 'cybersecurity', 'Security startup rounds and acquisitions.'),
            ('Enterprise SaaS Investment', 'saas', 'B2B software and enterprise platform funding.'),
            ('Climate Tech Funding', 'climate', 'Clean energy, sustainability, and green tech investments.'),
            ('Defense Tech Investments', 'defense', 'Defense, aerospace, and government tech funding.'),
            ('Unicorn Valuations', 'unicorns', 'Companies reaching billion-dollar valuations.'),
            ('M&A Activity', 'ma', 'Startup acquisitions, mergers, and strategic deals.'),
            ('Venture Capital Trends', 'vc', 'VC firm activity, fund raises, and investment thesis.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://news.crunchbase.com/{category}/',
                'summary': desc,
                'description': desc,
                'category': category,
                'sector': category,
                'source': 'Crunchbase News',
                'data_type': 'funding_topic',
                'tags': ['startups', 'funding', 'venture', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]

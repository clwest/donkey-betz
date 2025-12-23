"""
SeekingAlpha Spider - Investment Analysis Intelligence
=======================================================

Session 534: Simplified to work with spider network interface.
Aggregates investment analysis from financial news RSS feeds.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class SeekingAlphaSpider:
    """SeekingAlpha spider - investment analysis and market insights"""

    name = "seekingalpha"

    # Investment analysis RSS feeds
    RSS_FEEDS = {
        'marketwatch': 'https://feeds.content.dowjones.io/public/rss/mw_topstories',
        'investing': 'https://www.investing.com/rss/news.rss',
        'yahoo_finance': 'https://finance.yahoo.com/news/rssindex',
        'benzinga': 'https://www.benzinga.com/feed',
        'motley_fool': 'https://www.fool.com/feeds/index.aspx?id=foolwatch',
    }

    # Investment categories
    CATEGORIES = [
        ('Stocks', 'stocks', 'Stock picks and equity analysis.'),
        ('ETFs', 'etf', 'ETF and index fund coverage.'),
        ('Dividends', 'dividends', 'Dividend stocks and income investing.'),
        ('Growth', 'growth', 'Growth stocks and momentum plays.'),
        ('Macro', 'macro', 'Fed, rates, and economic analysis.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.investment_categories = {
            'stocks': ['stock', 'equity', 'shares', 'nasdaq', 'nyse', 's&p', 'dow'],
            'etf': ['etf', 'fund', 'index fund', 'vanguard', 'ishares', 'spdr'],
            'dividends': ['dividend', 'yield', 'payout', 'income', 'reit'],
            'growth': ['growth', 'tech stocks', 'momentum', 'high growth'],
            'value': ['value', 'undervalued', 'bargain', 'pe ratio', 'cheap'],
            'options': ['options', 'calls', 'puts', 'derivatives', 'volatility'],
            'macro': ['fed', 'interest rate', 'inflation', 'gdp', 'economy', 'recession'],
        }
        self.analysis_types = {
            'bullish': ['buy', 'bullish', 'upgrade', 'outperform', 'overweight', 'strong buy'],
            'bearish': ['sell', 'bearish', 'downgrade', 'underperform', 'underweight'],
            'neutral': ['hold', 'neutral', 'equal weight', 'market perform'],
            'earnings': ['earnings', 'revenue', 'profit', 'beat', 'miss', 'guidance'],
        }
        self.sectors = {
            'tech': ['technology', 'tech', 'software', 'saas', 'cloud', 'semiconductor'],
            'healthcare': ['healthcare', 'biotech', 'pharma', 'medical', 'drug'],
            'finance': ['bank', 'financial', 'insurance', 'fintech'],
            'energy': ['oil', 'gas', 'energy', 'renewable', 'solar', 'wind'],
            'consumer': ['retail', 'consumer', 'e-commerce', 'restaurant'],
        }

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch investment analysis from financial RSS feeds.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of investment analysis dictionaries
        """
        all_items = []
        seen_urls = set()

        # Fetch from RSS feeds
        for feed_name, feed_url in self.RSS_FEEDS.items():
            try:
                items = self._fetch_rss(feed_url, feed_name)
                for item in items:
                    if item['url'] not in seen_urls:
                        seen_urls.add(item['url'])
                        all_items.append(item)
            except Exception as e:
                logger.warning(f"Error fetching {feed_name} feed: {e}")

        # Add category links
        try:
            categories = self._get_category_links()
            all_items.extend(categories)
        except Exception as e:
            logger.warning(f"Error getting investment categories: {e}")

        # If all feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"SeekingAlpha spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch investment news from RSS feed."""
        items = []

        try:
            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:15]:
                title = entry.get('title', '')
                if not title:
                    continue

                url = entry.get('link', '')
                description = entry.get('summary', entry.get('description', ''))
                if description:
                    description = re.sub(r'<[^>]+>', '', description)[:500]

                # Analysis
                text = f"{title} {description}".lower()
                category = self._detect_category(text)
                analysis_type = self._detect_analysis_type(text)
                sector = self._detect_sector(text)
                sentiment = self._analyze_sentiment(text)

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': description,
                    'description': description,
                    'published': entry.get('published', ''),
                    'author': entry.get('author', ''),
                    'category': category,
                    'analysis_type': analysis_type,
                    'sector': sector,
                    'is_bullish': analysis_type == 'bullish',
                    'is_bearish': analysis_type == 'bearish',
                    'is_earnings': analysis_type == 'earnings',
                    'sentiment': sentiment,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'investment_analysis',
                    'platform': 'seekingalpha',
                    'tags': ['investing', 'stocks', category, analysis_type],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_category(self, text: str) -> str:
        """Detect investment category from text."""
        for category, keywords in self.investment_categories.items():
            if any(kw in text for kw in keywords):
                return category
        return 'general'

    def _detect_analysis_type(self, text: str) -> str:
        """Detect analysis type (bullish/bearish/neutral/earnings)."""
        for atype, keywords in self.analysis_types.items():
            if any(kw in text for kw in keywords):
                return atype
        return 'neutral'

    def _detect_sector(self, text: str) -> str:
        """Detect market sector from text."""
        for sector, keywords in self.sectors.items():
            if any(kw in text for kw in keywords):
                return sector
        return 'general'

    def _analyze_sentiment(self, text: str) -> str:
        """Analyze investment sentiment."""
        bullish = ['gain', 'rise', 'surge', 'rally', 'beat', 'record', 'upgrade', 'outperform']
        bearish = ['fall', 'drop', 'decline', 'miss', 'downgrade', 'warning', 'sell', 'loss']

        bull_count = sum(1 for word in bullish if word in text)
        bear_count = sum(1 for word in bearish if word in text)

        if bull_count > bear_count:
            return 'bullish'
        elif bear_count > bull_count:
            return 'bearish'
        return 'neutral'

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return investment category links."""
        return [
            {
                'title': f"Investing: {name}",
                'url': f'https://seekingalpha.com/{slug}',
                'link': f'https://seekingalpha.com/{slug}',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'SeekingAlpha',
                'data_type': 'investment_category',
                'platform': 'seekingalpha',
                'tags': ['investing', 'stocks', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('Stock Analysis', 'stocks', 'Individual stock picks and analysis.'),
            ('ETF Investing', 'etf', 'ETF and index fund coverage.'),
            ('Dividend Investing', 'dividends', 'Dividend stocks and income strategies.'),
            ('Growth Stocks', 'growth', 'High-growth stock opportunities.'),
            ('Market Outlook', 'macro', 'Fed policy and economic analysis.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://seekingalpha.com/{category}',
                'link': f'https://seekingalpha.com/{category}',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'SeekingAlpha',
                'data_type': 'investment_topic',
                'platform': 'seekingalpha',
                'tags': ['investing', 'stocks', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]

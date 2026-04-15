"""
Financial Spider - Financial Data & Market Intelligence
========================================================

Session 534: Simplified to work with spider network interface.
Uses yfinance for real-time market data and finance RSS feeds.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

# Try to import yfinance
try:
    import yfinance as yf
    from core.utils.yfinance_safe import make_timeout_session, fetch_with_timeout
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    logger.warning("yfinance not available - using RSS-only mode")


class FinancialIntelligenceSpider:
    """Financial spider - market data and financial intelligence"""

    name = "financial"

    # Finance news RSS feeds
    RSS_FEEDS = {
        'yahoo_finance': 'https://finance.yahoo.com/rss/',
        'marketwatch': 'https://feeds.marketwatch.com/marketwatch/topstories/',
        'investing': 'https://www.investing.com/rss/news.rss',
    }

    # Tracked symbols for market data
    TRACKED_SYMBOLS = [
        'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'NVDA', 'META',
        'SPY', 'QQQ', 'BTC-USD', 'ETH-USD'
    ]

    # Market sections
    SECTIONS = [
        ('Stocks', 'stocks', 'Stock market news and analysis.'),
        ('Crypto', 'crypto', 'Cryptocurrency and digital assets.'),
        ('Commodities', 'commodities', 'Gold, oil, and commodities.'),
        ('Forex', 'forex', 'Currency exchange and forex.'),
        ('Economy', 'economy', 'Economic news and indicators.'),
        ('Earnings', 'earnings', 'Company earnings reports.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.market_categories = {
            'stocks': ['stock', 'equity', 'shares', 'nasdaq', 'nyse', 's&p'],
            'crypto': ['bitcoin', 'crypto', 'ethereum', 'blockchain', 'btc'],
            'forex': ['forex', 'currency', 'dollar', 'euro', 'yen'],
            'commodities': ['oil', 'gold', 'commodity', 'crude', 'silver'],
            'economy': ['gdp', 'inflation', 'fed', 'interest rate', 'jobs'],
        }

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch financial data from multiple sources.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of financial data dictionaries
        """
        all_items = []
        seen_urls = set()

        # Fetch real-time market data if yfinance is available
        if YFINANCE_AVAILABLE:
            try:
                market_items = self._fetch_market_data()
                for item in market_items:
                    if item['url'] not in seen_urls:
                        seen_urls.add(item['url'])
                        all_items.append(item)
            except Exception as e:
                logger.warning(f"Error fetching market data: {e}")

        # Fetch from finance RSS feeds
        for feed_name, feed_url in self.RSS_FEEDS.items():
            try:
                items = self._fetch_rss(feed_url, feed_name)
                for item in items:
                    if item['url'] not in seen_urls:
                        seen_urls.add(item['url'])
                        all_items.append(item)
            except Exception as e:
                logger.warning(f"Error fetching {feed_name} feed: {e}")

        # Add section links
        try:
            sections = self._get_section_links()
            all_items.extend(sections)
        except Exception as e:
            logger.warning(f"Error getting financial sections: {e}")

        # If all sources fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Financial spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_market_data(self) -> List[Dict[str, Any]]:
        """Fetch real-time market data using yfinance."""
        items = []

        # Session 1084: reuse one timeout-enforced session across the
        # whole batch so HTTP connection pooling still works.
        safe_session = make_timeout_session(timeout=30.0)

        for symbol in self.TRACKED_SYMBOLS[:8]:  # Limit to avoid rate limits
            try:
                ticker = yf.Ticker(symbol, session=safe_session)
                # Session 1084: wrap info + history in executor backstop —
                # a single bad symbol shouldn't hang the batch for more
                # than 45s even if the session timeout is somehow bypassed.
                info = fetch_with_timeout(lambda t=ticker: t.info, timeout=45.0)
                hist = fetch_with_timeout(
                    lambda t=ticker: t.history(period="1d"),
                    timeout=45.0,
                )

                if hist.empty:
                    continue

                latest = hist.iloc[-1]
                price = float(latest['Close'])
                volume = int(latest['Volume'])

                # Calculate change
                prev_close = info.get('previousClose', price)
                change = ((price - prev_close) / prev_close * 100) if prev_close else 0
                change_str = f"+{change:.2f}%" if change >= 0 else f"{change:.2f}%"

                # Determine if crypto or stock
                is_crypto = '-USD' in symbol
                category = 'crypto' if is_crypto else 'stocks'

                items.append({
                    'title': f"{symbol}: ${price:,.2f} ({change_str})",
                    'url': f"https://finance.yahoo.com/quote/{symbol}",
                    'link': f"https://finance.yahoo.com/quote/{symbol}",
                    'summary': f"{info.get('shortName', symbol)} - Price: ${price:,.2f}, Volume: {volume:,}, Change: {change_str}",
                    'description': f"Market data for {symbol}. Market Cap: ${info.get('marketCap', 0):,.0f}",
                    'symbol': symbol,
                    'price': price,
                    'volume': volume,
                    'change_percent': change,
                    'market_cap': info.get('marketCap'),
                    'pe_ratio': info.get('trailingPE'),
                    '52_week_high': info.get('fiftyTwoWeekHigh'),
                    '52_week_low': info.get('fiftyTwoWeekLow'),
                    'category': category,
                    'is_crypto': is_crypto,
                    'source': 'Yahoo Finance',
                    'data_type': 'market_data',
                    'platform': 'financial',
                    'tags': ['finance', 'market', category, symbol],
                    'timestamp': datetime.now().isoformat(),
                })

            except Exception as e:
                logger.warning(f"Error fetching data for {symbol}: {e}")

        return items

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch articles from finance RSS feed."""
        items = []

        try:
            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:12]:
                title = entry.get('title', '')
                if not title:
                    continue

                url = entry.get('link', '')
                summary = entry.get('summary', entry.get('description', ''))
                if summary:
                    summary = re.sub(r'<[^>]+>', '', summary)[:500]

                # Detect market category
                text = f"{title} {summary}".lower()
                category = self._detect_category(text)
                is_high_impact = self._is_high_impact(text)

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': summary,
                    'description': summary,
                    'published': entry.get('published', ''),
                    'author': entry.get('author', feed_name.replace('_', ' ').title()),
                    'category': category,
                    'market_category': category,
                    'is_high_impact': is_high_impact,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'finance_article',
                    'platform': 'financial',
                    'tags': ['finance', 'markets', category],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_category(self, text: str) -> str:
        """Detect market category from text."""
        for category, keywords in self.market_categories.items():
            if any(kw in text for kw in keywords):
                return category
        return 'general'

    def _is_high_impact(self, text: str) -> bool:
        """Check if news is high impact."""
        impact_words = ['surge', 'plunge', 'crash', 'soar', 'tumble', 'record',
                        'breaking', 'alert', 'major', 'historic']
        return any(word in text for word in impact_words)

    def _get_section_links(self) -> List[Dict[str, Any]]:
        """Return financial section links."""
        return [
            {
                'title': f"Finance: {name}",
                'url': f'https://finance.yahoo.com/{slug}/',
                'link': f'https://finance.yahoo.com/{slug}/',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'Yahoo Finance',
                'data_type': 'finance_section',
                'platform': 'financial',
                'tags': ['finance', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.SECTIONS
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when all sources fail."""
        topics = [
            ('Stock Market', 'stocks', 'Stock market news and analysis.'),
            ('Cryptocurrency', 'crypto', 'Digital asset news.'),
            ('Economic News', 'economy', 'Economic indicators and data.'),
            ('Commodities', 'commodities', 'Gold, oil, and more.'),
            ('Earnings Reports', 'earnings', 'Company earnings.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://finance.yahoo.com/{category}/',
                'link': f'https://finance.yahoo.com/{category}/',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'Yahoo Finance',
                'data_type': 'finance_topic',
                'platform': 'financial',
                'tags': ['finance', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]

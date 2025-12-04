"""
Polygon Spider - Financial Market Data Intelligence
===================================================

Session 343: Phase 1 Spider Expansion
Polygon.io provides comprehensive stock market data with a free tier.
"""

import os
import aiohttp
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class PolygonSpider(BaseIntelligenceSpider):
    """Polygon.io stock market data spider - real-time and historical market data"""

    BASE_URL = 'https://api.polygon.io'

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)
        self.api_key = os.getenv('POLYGON_API_KEY', '')

        # Top stocks to track
        self.tracked_tickers = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA',
            'BRK.B', 'JPM', 'V', 'UNH', 'XOM', 'JNJ', 'WMT', 'PG'
        ]

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch market data from Polygon.io"""
        if not self.api_key:
            self.logger.warning("POLYGON_API_KEY not set")
            return None

        try:
            all_data = {
                'ticker_snapshots': [],
                'market_news': [],
                'gainers_losers': None,
            }

            async with aiohttp.ClientSession() as session:
                # Get ticker snapshots for tracked stocks
                for ticker in self.tracked_tickers[:5]:  # Limit to 5 for rate limits
                    snapshot = await self._fetch_ticker_snapshot(session, ticker)
                    if snapshot:
                        all_data['ticker_snapshots'].append(snapshot)

                # Get gainers and losers
                gainers_losers = await self._fetch_gainers_losers(session)
                if gainers_losers:
                    all_data['gainers_losers'] = gainers_losers

                # Get market news
                news = await self._fetch_market_news(session)
                if news:
                    all_data['market_news'] = news

            return all_data

        except Exception as e:
            self.logger.error(f"Error fetching Polygon data: {e}")
            return None

    async def _fetch_ticker_snapshot(self, session: aiohttp.ClientSession, ticker: str) -> Optional[Dict[str, Any]]:
        """Fetch snapshot for a single ticker"""
        try:
            url = f"{self.BASE_URL}/v2/snapshot/locale/us/markets/stocks/tickers/{ticker}"
            params = {'apiKey': self.api_key}

            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('status') == 'OK' and data.get('ticker'):
                        ticker_data = data['ticker']
                        return {
                            'ticker': ticker,
                            'name': ticker_data.get('name', ticker),
                            'price': ticker_data.get('day', {}).get('c', 0),
                            'change': ticker_data.get('todaysChange', 0),
                            'change_percent': ticker_data.get('todaysChangePerc', 0),
                            'volume': ticker_data.get('day', {}).get('v', 0),
                            'high': ticker_data.get('day', {}).get('h', 0),
                            'low': ticker_data.get('day', {}).get('l', 0),
                            'open': ticker_data.get('day', {}).get('o', 0),
                            'previous_close': ticker_data.get('prevDay', {}).get('c', 0),
                        }
        except Exception as e:
            self.logger.warning(f"Error fetching {ticker}: {e}")
        return None

    async def _fetch_gainers_losers(self, session: aiohttp.ClientSession) -> Optional[Dict[str, Any]]:
        """Fetch market gainers and losers"""
        try:
            url = f"{self.BASE_URL}/v2/snapshot/locale/us/markets/stocks/gainers"
            params = {'apiKey': self.api_key}

            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    gainers = []
                    for ticker in data.get('tickers', [])[:10]:
                        gainers.append({
                            'ticker': ticker.get('ticker'),
                            'change_percent': ticker.get('todaysChangePerc', 0),
                            'price': ticker.get('day', {}).get('c', 0),
                        })

            # Fetch losers
            url = f"{self.BASE_URL}/v2/snapshot/locale/us/markets/stocks/losers"
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    losers = []
                    for ticker in data.get('tickers', [])[:10]:
                        losers.append({
                            'ticker': ticker.get('ticker'),
                            'change_percent': ticker.get('todaysChangePerc', 0),
                            'price': ticker.get('day', {}).get('c', 0),
                        })

            return {'gainers': gainers, 'losers': losers}

        except Exception as e:
            self.logger.warning(f"Error fetching gainers/losers: {e}")
        return None

    async def _fetch_market_news(self, session: aiohttp.ClientSession) -> List[Dict[str, Any]]:
        """Fetch market news"""
        try:
            url = f"{self.BASE_URL}/v2/reference/news"
            params = {'apiKey': self.api_key, 'limit': 20}

            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    news = []
                    for article in data.get('results', []):
                        news.append({
                            'title': article.get('title', ''),
                            'description': article.get('description', ''),
                            'publisher': article.get('publisher', {}).get('name', ''),
                            'url': article.get('article_url', ''),
                            'tickers': article.get('tickers', []),
                            'published': article.get('published_utc', ''),
                        })
                    return news
        except Exception as e:
            self.logger.warning(f"Error fetching news: {e}")
        return []

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process Polygon market data"""
        try:
            snapshots = raw_data.get('ticker_snapshots', [])
            gainers_losers = raw_data.get('gainers_losers', {})
            news = raw_data.get('market_news', [])

            # Calculate market sentiment from gainers/losers
            market_sentiment = 'neutral'
            if gainers_losers:
                gainers = gainers_losers.get('gainers', [])
                losers = gainers_losers.get('losers', [])
                if gainers and losers:
                    avg_gain = sum(g.get('change_percent', 0) for g in gainers) / len(gainers) if gainers else 0
                    avg_loss = abs(sum(l.get('change_percent', 0) for l in losers) / len(losers)) if losers else 0
                    if avg_gain > avg_loss * 1.2:
                        market_sentiment = 'bullish'
                    elif avg_loss > avg_gain * 1.2:
                        market_sentiment = 'bearish'

            content = {
                'ticker_snapshots': snapshots,
                'gainers_losers': gainers_losers,
                'market_news': news,
                'market_sentiment': market_sentiment,
                'summary': {
                    'tickers_tracked': len(snapshots),
                    'news_articles': len(news),
                    'market_sentiment': market_sentiment,
                }
            }

            quality_score = min(1.0, (len(snapshots) / 10 + len(news) / 20) / 2 + 0.3)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='polygon.io',
                data_type='financial_market',
                content=content,
                metadata={
                    'tickers_tracked': len(snapshots),
                    'news_count': len(news),
                    'source': 'polygon',
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['stocks', 'finance', 'market', 'trading', 'investing'],
                target_agents=['research_agent', 'financial_agent'],
                target_advisors=['financial_analyst', 'market_strategist']
            )

        except Exception as e:
            self.logger.error(f"Error processing Polygon data: {e}")
            return None

    def get_required_fields(self) -> List[str]:
        return ['ticker']

    def get_relevance_keywords(self) -> List[str]:
        return ['stock', 'market', 'finance', 'trading', 'investing', 'earnings']

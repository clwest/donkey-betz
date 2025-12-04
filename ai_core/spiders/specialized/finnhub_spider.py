"""
Finnhub Spider - Financial Market Intelligence
==============================================

Session 343: Phase 1 Spider Expansion
Finnhub provides real-time stock data, forex, crypto with free tier (60 calls/min).
"""

import os
import aiohttp
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class FinnhubSpider(BaseIntelligenceSpider):
    """Finnhub financial data spider - stocks, forex, crypto, company fundamentals"""

    BASE_URL = 'https://finnhub.io/api/v1'

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)
        self.api_key = os.getenv('FINNHUB_API_KEY', '')

        # Top stocks to track
        self.tracked_symbols = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA',
            'JPM', 'V', 'UNH'
        ]

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch financial data from Finnhub"""
        if not self.api_key:
            self.logger.warning("FINNHUB_API_KEY not set")
            return None

        try:
            all_data = {
                'quotes': [],
                'market_news': [],
                'company_news': [],
                'earnings_calendar': [],
            }

            async with aiohttp.ClientSession() as session:
                # Get quotes for tracked symbols
                for symbol in self.tracked_symbols[:5]:  # Limit for rate limits
                    quote = await self._fetch_quote(session, symbol)
                    if quote:
                        all_data['quotes'].append(quote)

                # Get market news
                news = await self._fetch_market_news(session)
                if news:
                    all_data['market_news'] = news

                # Get earnings calendar
                earnings = await self._fetch_earnings_calendar(session)
                if earnings:
                    all_data['earnings_calendar'] = earnings

            return all_data

        except Exception as e:
            self.logger.error(f"Error fetching Finnhub data: {e}")
            return None

    async def _fetch_quote(self, session: aiohttp.ClientSession, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch quote for a single symbol"""
        try:
            url = f"{self.BASE_URL}/quote"
            params = {'symbol': symbol, 'token': self.api_key}

            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('c'):  # Current price exists
                        return {
                            'symbol': symbol,
                            'current': data.get('c', 0),
                            'high': data.get('h', 0),
                            'low': data.get('l', 0),
                            'open': data.get('o', 0),
                            'previous_close': data.get('pc', 0),
                            'change': data.get('d', 0),
                            'change_percent': data.get('dp', 0),
                            'timestamp': data.get('t', 0),
                        }
        except Exception as e:
            self.logger.warning(f"Error fetching quote for {symbol}: {e}")
        return None

    async def _fetch_market_news(self, session: aiohttp.ClientSession) -> List[Dict[str, Any]]:
        """Fetch general market news"""
        try:
            url = f"{self.BASE_URL}/news"
            params = {'category': 'general', 'token': self.api_key}

            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    news = []
                    for article in data[:15]:
                        news.append({
                            'headline': article.get('headline', ''),
                            'summary': article.get('summary', ''),
                            'source': article.get('source', ''),
                            'url': article.get('url', ''),
                            'datetime': article.get('datetime', 0),
                            'category': article.get('category', ''),
                            'related': article.get('related', ''),
                        })
                    return news
        except Exception as e:
            self.logger.warning(f"Error fetching market news: {e}")
        return []

    async def _fetch_earnings_calendar(self, session: aiohttp.ClientSession) -> List[Dict[str, Any]]:
        """Fetch upcoming earnings"""
        try:
            from datetime import timedelta
            today = datetime.now().strftime('%Y-%m-%d')
            next_week = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')

            url = f"{self.BASE_URL}/calendar/earnings"
            params = {'from': today, 'to': next_week, 'token': self.api_key}

            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    earnings = []
                    for entry in data.get('earningsCalendar', [])[:20]:
                        earnings.append({
                            'symbol': entry.get('symbol', ''),
                            'date': entry.get('date', ''),
                            'eps_estimate': entry.get('epsEstimate', 0),
                            'eps_actual': entry.get('epsActual'),
                            'revenue_estimate': entry.get('revenueEstimate', 0),
                            'hour': entry.get('hour', ''),
                        })
                    return earnings
        except Exception as e:
            self.logger.warning(f"Error fetching earnings calendar: {e}")
        return []

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process Finnhub financial data"""
        try:
            quotes = raw_data.get('quotes', [])
            news = raw_data.get('market_news', [])
            earnings = raw_data.get('earnings_calendar', [])

            # Calculate overall market direction
            positive_moves = sum(1 for q in quotes if q.get('change_percent', 0) > 0)
            negative_moves = len(quotes) - positive_moves
            market_direction = 'bullish' if positive_moves > negative_moves else 'bearish' if negative_moves > positive_moves else 'mixed'

            # Top movers
            sorted_quotes = sorted(quotes, key=lambda x: abs(x.get('change_percent', 0)), reverse=True)
            top_movers = sorted_quotes[:5]

            content = {
                'quotes': quotes,
                'market_news': news,
                'earnings_calendar': earnings,
                'market_direction': market_direction,
                'top_movers': top_movers,
                'summary': {
                    'symbols_tracked': len(quotes),
                    'news_articles': len(news),
                    'upcoming_earnings': len(earnings),
                    'market_direction': market_direction,
                }
            }

            quality_score = min(1.0, (len(quotes) / 10 + len(news) / 15) / 2 + 0.3)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='finnhub.io',
                data_type='financial_market',
                content=content,
                metadata={
                    'symbols_tracked': len(quotes),
                    'news_count': len(news),
                    'earnings_count': len(earnings),
                    'source': 'finnhub',
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['stocks', 'finance', 'market', 'earnings', 'news'],
                target_agents=['research_agent', 'financial_agent'],
                target_advisors=['financial_analyst', 'market_strategist']
            )

        except Exception as e:
            self.logger.error(f"Error processing Finnhub data: {e}")
            return None

    def get_required_fields(self) -> List[str]:
        return ['symbol']

    def get_relevance_keywords(self) -> List[str]:
        return ['stock', 'market', 'finance', 'earnings', 'investing', 'trading']

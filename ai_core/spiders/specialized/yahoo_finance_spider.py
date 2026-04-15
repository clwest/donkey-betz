"""
Yahoo Finance Stock Market Data Spider
=======================================

Session 344: Uses the yfinance library for reliable stock data fetching.

Fetches stock market data from Yahoo Finance:
- Market indices (S&P 500, Dow Jones, NASDAQ)
- Major tech stocks (AAPL, MSFT, GOOGL, etc.)
- Trending/popular stocks

No API key required - uses yfinance library.
"""

import yfinance as yf

from core.utils.yfinance_safe import make_timeout_session, fetch_with_timeout
from typing import Dict, List, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class YahooFinanceSpider:
    """Spider for fetching stock market data using yfinance library"""

    name = "yahoo_finance"

    # Session 981: Sector-diverse default symbols (was tech-heavy)
    DEFAULT_SYMBOLS = [
        # Market Indices
        "^GSPC",   # S&P 500
        "^DJI",    # Dow Jones
        "^IXIC",   # NASDAQ
        # Tech (3)
        "AAPL",    # Apple
        "MSFT",    # Microsoft
        "NVDA",    # NVIDIA
        # Finance (3)
        "JPM",     # JPMorgan
        "GS",      # Goldman Sachs
        "V",       # Visa
        # Healthcare (2)
        "UNH",     # UnitedHealth
        "LLY",     # Eli Lilly
        # Consumer (2)
        "WMT",     # Walmart
        "COST",    # Costco
        # Energy (2)
        "XOM",     # Exxon
        "CVX",     # Chevron
        # Industrial (2)
        "CAT",     # Caterpillar
        "BA",      # Boeing
    ]

    def __init__(self):
        pass

    def fetch_data(self, max_results: int = 50, symbols: List[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch stock market data from Yahoo Finance using yfinance

        Args:
            max_results: Maximum number of stocks to fetch
            symbols: Optional list of specific symbols to fetch

        Returns:
            List of stock data dictionaries
        """
        target_symbols = symbols or self.DEFAULT_SYMBOLS

        # Limit symbols to max_results
        target_symbols = target_symbols[:max_results]

        all_data = []

        # Fetch quotes using yfinance
        # Session 1084: Inject a timeout-enforcing requests.Session to
        # prevent CLOSE_WAIT hangs. yfinance 0.2.65 uses requests with no
        # default timeout, so a half-closed upstream connection blocks
        # recv() forever and wedges the entire Celery worker process. The
        # session forces (connect=5s, read=30s) on every underlying HTTP
        # call. Per-ticker info lookups are also wrapped in a hard
        # executor timeout as a backstop.
        safe_session = make_timeout_session(timeout=30.0)
        try:
            logger.info(f"Fetching {len(target_symbols)} symbols from Yahoo Finance")

            # Use yfinance Tickers to batch fetch
            tickers = yf.Tickers(" ".join(target_symbols), session=safe_session)

            for symbol in target_symbols:
                try:
                    ticker = tickers.tickers.get(symbol)
                    if not ticker:
                        continue

                    # Session 1084: ticker.info can make many network calls;
                    # wrap in a hard backstop timeout so a single bad symbol
                    # can't hang the whole fetch batch.
                    info = fetch_with_timeout(lambda t=ticker: t.info, timeout=45.0)

                    # Get price data
                    price = info.get('regularMarketPrice') or info.get('currentPrice', 0)
                    prev_close = info.get('regularMarketPreviousClose') or info.get('previousClose', 0)
                    change = price - prev_close if price and prev_close else 0
                    pct_change = (change / prev_close * 100) if prev_close else 0

                    # Determine if this is an index
                    is_index = symbol.startswith('^')
                    data_type = 'market_index' if is_index else 'stock'

                    # Get name
                    name = info.get('shortName') or info.get('longName') or symbol

                    all_data.append({
                        'symbol': symbol.replace('^', ''),  # Clean up index symbols for display
                        'name': name,
                        'current_price': price,
                        'price': price,  # Alias
                        'change': round(change, 2) if change else 0,
                        'change_percent': round(pct_change, 2) if pct_change else 0,
                        'percent_change': round(pct_change, 2) if pct_change else 0,  # Alias
                        'market_cap': info.get('marketCap'),
                        'volume': info.get('regularMarketVolume') or info.get('volume'),
                        'high_24h': info.get('regularMarketDayHigh') or info.get('dayHigh'),
                        'low_24h': info.get('regularMarketDayLow') or info.get('dayLow'),
                        'open': info.get('regularMarketOpen') or info.get('open'),
                        'previous_close': prev_close,
                        'fifty_two_week_high': info.get('fiftyTwoWeekHigh'),
                        'fifty_two_week_low': info.get('fiftyTwoWeekLow'),
                        'sector': info.get('sector', 'N/A'),
                        'industry': info.get('industry', 'N/A'),
                        'data_type': data_type,
                        'source': 'yahoo_finance',
                        'type': 'item',
                        'tags': self._extract_tags(symbol, pct_change, is_index),
                        'fetched_at': datetime.now().isoformat(),
                    })

                except Exception as e:
                    logger.warning(f"Error fetching {symbol}: {e}")
                    continue

            logger.info(f"Yahoo Finance spider fetched {len(all_data)} stock quotes")

        except Exception as e:
            logger.error(f"Error in Yahoo Finance fetch: {e}")

        return all_data

    def _extract_tags(self, symbol: str, pct_change: float, is_index: bool = False) -> List[str]:
        """Extract relevant tags for the stock"""
        tags = ['equity']

        if is_index:
            tags.append('index')
            tags.append('market')
        else:
            tags.append('stock')

        if symbol:
            tags.append(symbol.replace('^', '').lower())

        # Performance tags
        if pct_change:
            if pct_change > 5:
                tags.append('strong_gainer')
            elif pct_change > 2:
                tags.append('gainer')
            elif pct_change < -5:
                tags.append('strong_loser')
            elif pct_change < -2:
                tags.append('loser')

            # Volatility
            if abs(pct_change) > 10:
                tags.append('highly_volatile')
            elif abs(pct_change) > 5:
                tags.append('volatile')

        return tags


# For direct testing
if __name__ == "__main__":
    spider = YahooFinanceSpider()
    data = spider.fetch_data(max_results=10)
    print(f"Fetched {len(data)} stocks")
    for d in data[:5]:
        print(f"{d['symbol']}: ${d['current_price']:,.2f} ({d['change_percent']:+.2f}%)")

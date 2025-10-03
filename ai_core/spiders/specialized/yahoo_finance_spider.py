"""
Yahoo Finance Stock Market Data Spider
=======================================

Fetches stock market data from Yahoo Finance (free, no API key required).

Data Sources:
- Yahoo Finance trending stocks
- Market indices (S&P 500, Dow, NASDAQ)
- Top gainers/losers

No API key required - uses public web scraping.
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Any
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


class YahooFinanceSpider:
    """Spider for fetching stock market data from Yahoo Finance"""

    name = "yahoo_finance"
    base_url = "https://finance.yahoo.com"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch stock market data

        Args:
            max_results: Maximum number of stocks to fetch

        Returns:
            List of stock data
        """
        all_data = []

        # Fetch trending stocks
        all_data.extend(self._fetch_trending_stocks(max_results // 3))

        # Fetch top gainers
        all_data.extend(self._fetch_gainers_losers('gainers', max_results // 3))

        # Fetch market indices
        all_data.extend(self._fetch_market_indices())

        return all_data[:max_results]

    def _fetch_trending_stocks(self, limit: int = 15) -> List[Dict[str, Any]]:
        """Fetch trending stocks from Yahoo Finance"""
        try:
            url = f"{self.base_url}/trending-tickers"
            logger.info("Fetching trending stocks from Yahoo Finance")

            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            stocks = []

            # Find trending stock table rows
            table = soup.find('table')
            if table:
                rows = table.find_all('tr')[1:limit+1]  # Skip header row

                for row in rows:
                    try:
                        cells = row.find_all('td')
                        if len(cells) >= 5:
                            symbol = cells[0].get_text(strip=True)
                            name = cells[1].get_text(strip=True) if len(cells) > 1 else ''
                            price_text = cells[2].get_text(strip=True) if len(cells) > 2 else '0'
                            change_text = cells[3].get_text(strip=True) if len(cells) > 3 else '0'
                            pct_change_text = cells[4].get_text(strip=True) if len(cells) > 4 else '0'

                            # Parse numeric values
                            try:
                                price = float(price_text.replace(',', ''))
                            except:
                                price = 0

                            try:
                                change = float(change_text.replace('+', '').replace(',', ''))
                            except:
                                change = 0

                            try:
                                pct_change = float(pct_change_text.replace('%', '').replace('+', ''))
                            except:
                                pct_change = 0

                            stocks.append({
                                'symbol': symbol,
                                'name': name,
                                'price': price,
                                'change': change,
                                'percent_change': pct_change,
                                'data_type': 'trending_stock',
                                'source': 'Yahoo Finance Trending',
                                'tags': self._extract_tags(symbol, pct_change),
                                'timestamp': datetime.now().isoformat(),
                            })

                    except Exception as e:
                        logger.warning(f"Error parsing trending stock row: {e}")
                        continue

            logger.info(f"Fetched {len(stocks)} trending stocks from Yahoo Finance")
            return stocks

        except Exception as e:
            logger.error(f"Error fetching trending stocks: {e}")
            return []

    def _fetch_gainers_losers(self, category: str = 'gainers', limit: int = 15) -> List[Dict[str, Any]]:
        """Fetch top gainers or losers"""
        try:
            url = f"{self.base_url}/{category}"
            logger.info(f"Fetching {category} from Yahoo Finance")

            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            stocks = []

            # Find gainers/losers table
            table = soup.find('table')
            if table:
                rows = table.find_all('tr')[1:limit+1]  # Skip header

                for row in rows:
                    try:
                        cells = row.find_all('td')
                        if len(cells) >= 5:
                            symbol = cells[0].get_text(strip=True)
                            name = cells[1].get_text(strip=True) if len(cells) > 1 else ''
                            price_text = cells[2].get_text(strip=True) if len(cells) > 2 else '0'
                            change_text = cells[3].get_text(strip=True) if len(cells) > 3 else '0'
                            pct_change_text = cells[4].get_text(strip=True) if len(cells) > 4 else '0'

                            try:
                                price = float(price_text.replace(',', ''))
                            except:
                                price = 0

                            try:
                                change = float(change_text.replace('+', '').replace(',', ''))
                            except:
                                change = 0

                            try:
                                pct_change = float(pct_change_text.replace('%', '').replace('+', ''))
                            except:
                                pct_change = 0

                            stocks.append({
                                'symbol': symbol,
                                'name': name,
                                'price': price,
                                'change': change,
                                'percent_change': pct_change,
                                'data_type': f'stock_{category}',
                                'source': f'Yahoo Finance {category.title()}',
                                'tags': self._extract_tags(symbol, pct_change, category),
                                'timestamp': datetime.now().isoformat(),
                            })

                    except Exception as e:
                        logger.warning(f"Error parsing {category} row: {e}")
                        continue

            logger.info(f"Fetched {len(stocks)} {category} from Yahoo Finance")
            return stocks

        except Exception as e:
            logger.error(f"Error fetching {category}: {e}")
            return []

    def _fetch_market_indices(self) -> List[Dict[str, Any]]:
        """Fetch major market indices"""
        indices_symbols = [
            ('^GSPC', 'S&P 500'),
            ('^DJI', 'Dow Jones'),
            ('^IXIC', 'NASDAQ'),
            ('^RUT', 'Russell 2000'),
        ]

        indices_data = []

        for symbol, name in indices_symbols:
            try:
                url = f"{self.base_url}/quote/{symbol}"
                response = self.session.get(url, timeout=20)
                response.raise_for_status()

                soup = BeautifulSoup(response.content, 'html.parser')

                # Try to extract index data from page
                price_elem = soup.find('fin-streamer', {'data-symbol': symbol, 'data-field': 'regularMarketPrice'})
                change_elem = soup.find('fin-streamer', {'data-symbol': symbol, 'data-field': 'regularMarketChange'})
                pct_elem = soup.find('fin-streamer', {'data-symbol': symbol, 'data-field': 'regularMarketChangePercent'})

                price = float(price_elem.get_text(strip=True).replace(',', '')) if price_elem else 0
                change = float(change_elem.get_text(strip=True).replace('+', '').replace(',', '')) if change_elem else 0
                pct_change = float(pct_elem.get_text(strip=True).replace('%', '').replace('+', '')) if pct_elem else 0

                indices_data.append({
                    'symbol': symbol,
                    'name': name,
                    'price': price,
                    'change': change,
                    'percent_change': pct_change,
                    'data_type': 'market_index',
                    'source': 'Yahoo Finance',
                    'tags': ['index', 'market', name.lower().replace(' ', '_')],
                    'timestamp': datetime.now().isoformat(),
                })

            except Exception as e:
                logger.warning(f"Error fetching {name} ({symbol}): {e}")
                continue

        logger.info(f"Fetched {len(indices_data)} market indices")
        return indices_data

    def _extract_tags(self, symbol: str, pct_change: float, category: str = '') -> List[str]:
        """Extract relevant tags"""
        tags = ['stock', 'equity']

        if symbol:
            tags.append(symbol)

        # Performance tags
        if pct_change > 5:
            tags.append('strong_gainer')
        elif pct_change > 2:
            tags.append('gainer')
        elif pct_change < -5:
            tags.append('strong_loser')
        elif pct_change < -2:
            tags.append('loser')

        if category:
            tags.append(category)

        # Volatility
        if abs(pct_change) > 10:
            tags.append('highly_volatile')
        elif abs(pct_change) > 5:
            tags.append('volatile')

        return tags

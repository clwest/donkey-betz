"""
Financial Intelligence Spider - Elite Financial Data Gathering
=============================================================

Specialized spider for gathering financial intelligence for Buffett-style advisors
and financial analysis agents. Focuses on high-quality financial data, SEC filings,
earnings reports, and market fundamentals.

Target Advisors:
- Warren Buffett (value investing)
- Ray Dalio (macroeconomic analysis)
- Financial Strategist (portfolio management)
- Crypto Expert (digital assets)
- Options Master (derivatives trading)
"""

import re
import json
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
import yfinance as yf
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData
from ..web_request_layer import web_request_layer


class FinancialIntelligenceSpider(BaseIntelligenceSpider):
    """
    Elite financial intelligence gathering spider.

    Specializes in:
    - SEC EDGAR filings (10-K, 10-Q, 8-K)
    - Real-time stock data and fundamentals
    - Earnings reports and analyst estimates
    - Market indicators and economic data
    - Crypto market analysis
    - Options flow data
    """

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        # Financial-specific configuration
        self.tracked_symbols = [
            'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX',
            'BRK-A', 'BRK-B', 'JPM', 'BAC', 'WFC', 'GS', 'MS',
            'SPY', 'QQQ', 'IWM', 'VTI', 'ARKK', 'ARKW'
        ]

        self.crypto_symbols = [
            'BTC-USD', 'ETH-USD', 'ADA-USD', 'DOT-USD', 'LINK-USD',
            'SOL-USD', 'AVAX-USD', 'MATIC-USD', 'ALGO-USD'
        ]

        # Financial data quality requirements
        self.required_financial_fields = [
            'symbol', 'price', 'volume', 'market_cap'
        ]

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process financial data into structured intelligence"""
        try:
            # Determine data type based on source
            if 'sec.gov' in target.url:
                return await self._process_sec_filing(raw_data, target)
            elif 'finance.yahoo.com' in target.url:
                return await self._process_yahoo_finance(raw_data, target)
            elif any(crypto in target.url for crypto in ['binance', 'coinbase', 'crypto']):
                return await self._process_crypto_data(raw_data, target)
            elif 'polygon.io' in target.url:
                return await self._process_market_data(raw_data, target)
            else:
                return await self._process_general_financial(raw_data, target)

        except Exception as e:
            self.logger.error(f"Error processing financial data: {e}")
            return None

    async def _process_sec_filing(self, data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process SEC EDGAR filing data"""
        try:
            # Extract filing information
            filing_info = {}

            if 'content' in data:
                soup = BeautifulSoup(data['content'], 'html.parser')

                # Extract key filing details
                filing_info = {
                    'filing_type': self._extract_filing_type(soup),
                    'company': self._extract_company_name(soup),
                    'ticker': self._extract_ticker_symbol(soup),
                    'filing_date': self._extract_filing_date(soup),
                    'period_end': self._extract_period_end(soup),
                    'key_metrics': self._extract_financial_metrics(soup),
                    'management_discussion': self._extract_md_a(soup),
                    'risk_factors': self._extract_risk_factors(soup)
                }

            # Determine quality score
            quality_score = self._calculate_sec_quality(filing_info)

            # Create intelligence data
            intelligence = IntelligenceData(
                spider_id=self.spider_id,
                source_url=target.url,
                data_type="sec_filing",
                content=filing_info,
                metadata={
                    'filing_type': filing_info.get('filing_type'),
                    'company': filing_info.get('company'),
                    'ticker': filing_info.get('ticker'),
                    'data_freshness': 'regulatory'
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['sec', 'filing', 'financial', 'regulatory'],
                target_agents=['financial_analysis_agent', 'value_investing_agent'],
                target_advisors=['warren_buffett', 'financial_strategist', 'legal_counsel']
            )

            return intelligence

        except Exception as e:
            self.logger.error(f"Error processing SEC filing: {e}")
            return None

    async def fetch_real_financial_data(self, symbols: List[str]) -> Dict[str, Any]:
        """Fetch real financial data from multiple sources"""
        financial_data = {}

        # Initialize web request layer
        await web_request_layer.initialize()

        # 1. Fetch from Alpha Vantage (if API key available)
        alpha_vantage_key = os.environ.get('ALPHA_VANTAGE_KEY')
        if alpha_vantage_key:
            for symbol in symbols[:3]:  # Limit to avoid rate limits
                url = f"https://www.alphavantage.co/query"
                params = {
                    'function': 'GLOBAL_QUOTE',
                    'symbol': symbol,
                    'apikey': alpha_vantage_key
                }
                response = await web_request_layer.fetch(url, params=params)
                if response['json'] and 'Global Quote' in response['json']:
                    quote = response['json']['Global Quote']
                    financial_data[symbol] = {
                        'source': 'alpha_vantage',
                        'price': float(quote.get('05. price', 0)),
                        'volume': int(quote.get('06. volume', 0)),
                        'change': quote.get('09. change'),
                        'change_percent': quote.get('10. change percent')
                    }

        # 2. Fetch from IEX Cloud (sandbox/free tier)
        for symbol in symbols[:5]:
            # Using IEX sandbox endpoint (free)
            url = f"https://sandbox.iexapis.com/stable/stock/{symbol.lower()}/quote"
            params = {'token': 'Tpk_053b8dd1b9684e2c9816ab4f6b8a1e7a'}  # Sandbox token
            response = await web_request_layer.fetch(url, params=params)
            if response['json']:
                quote = response['json']
                financial_data[f"{symbol}_iex"] = {
                    'source': 'iex_cloud',
                    'price': quote.get('latestPrice'),
                    'volume': quote.get('volume'),
                    'market_cap': quote.get('marketCap'),
                    'pe_ratio': quote.get('peRatio'),
                    '52_week_high': quote.get('week52High'),
                    '52_week_low': quote.get('week52Low')
                }

        # 3. Fetch crypto data from CoinGecko (no auth required)
        crypto_url = "https://api.coingecko.com/api/v3/simple/price"
        crypto_params = {
            'ids': 'bitcoin,ethereum,cardano,polkadot,chainlink',
            'vs_currencies': 'usd',
            'include_market_cap': 'true',
            'include_24hr_vol': 'true',
            'include_24hr_change': 'true'
        }
        crypto_response = await web_request_layer.fetch(crypto_url, params=crypto_params)
        if crypto_response['json']:
            for coin, data in crypto_response['json'].items():
                financial_data[f"crypto_{coin}"] = {
                    'source': 'coingecko',
                    'price': data.get('usd'),
                    'market_cap': data.get('usd_market_cap'),
                    'volume_24h': data.get('usd_24h_vol'),
                    'change_24h': data.get('usd_24h_change')
                }

        # 4. Fetch market news from NewsAPI (if key available)
        news_api_key = os.environ.get('NEWS_API_KEY')
        if news_api_key:
            news_url = "https://newsapi.org/v2/top-headlines"
            news_params = {
                'category': 'business',
                'country': 'us',
                'apiKey': news_api_key,
                'pageSize': 5
            }
            news_response = await web_request_layer.fetch(news_url, params=news_params)
            if news_response['json'] and 'articles' in news_response['json']:
                financial_data['market_news'] = {
                    'source': 'newsapi',
                    'articles': news_response['json']['articles']
                }

        return financial_data

    async def _process_yahoo_finance(self, data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process Yahoo Finance data with real API calls"""
        try:
            # Extract stock symbols from URL or use tracked symbols
            symbols = self._extract_symbols_from_url(target.url) or self.tracked_symbols[:5]

            # Fetch real financial data from multiple sources
            financial_data = await self.fetch_real_financial_data(symbols)

            # Also try yfinance for additional data
            for symbol in symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    info = ticker.info
                    hist = ticker.history(period="1d")

                    if not hist.empty:
                        latest = hist.iloc[-1]
                        financial_data[f"{symbol}_yfinance"] = {
                            'source': 'yfinance',
                            'price': float(latest['Close']),
                            'volume': int(latest['Volume']),
                            'open': float(latest['Open']),
                            'high': float(latest['High']),
                            'low': float(latest['Low']),
                            'market_cap': info.get('marketCap'),
                            'pe_ratio': info.get('trailingPE'),
                            'forward_pe': info.get('forwardPE'),
                            'peg_ratio': info.get('pegRatio'),
                            'price_to_book': info.get('priceToBook'),
                            'dividend_yield': info.get('dividendYield'),
                            'beta': info.get('beta'),
                            '52_week_high': info.get('fiftyTwoWeekHigh'),
                            '52_week_low': info.get('fiftyTwoWeekLow'),
                            'analyst_target': info.get('targetMeanPrice'),
                            'recommendation': info.get('recommendationMean')
                        }
                except Exception as e:
                    self.logger.warning(f"Failed to get yfinance data for {symbol}: {e}")

            # Calculate quality score
            quality_score = self._calculate_market_data_quality(financial_data)

            # Create intelligence data
            intelligence = IntelligenceData(
                spider_id=self.spider_id,
                source_url=target.url,
                data_type="market_data",
                content=financial_data,
                metadata={
                    'symbols_count': len(financial_data),
                    'data_source': 'yahoo_finance',
                    'data_freshness': 'real_time'
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['stocks', 'market_data', 'real_time', 'fundamentals'],
                target_agents=['trading_agents', 'value_investing_agent', 'momentum_trading_agent'],
                target_advisors=['warren_buffett', 'ray_dalio', 'options_master']
            )

            return intelligence

        except Exception as e:
            self.logger.error(f"Error processing Yahoo Finance data: {e}")
            return None

    async def _process_crypto_data(self, data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process cryptocurrency data"""
        try:
            crypto_data = {}

            # Process different crypto data sources
            if isinstance(data, dict):
                # Handle API responses
                if 'price' in data:
                    crypto_data = data
                elif 'data' in data:
                    crypto_data = data['data']
                else:
                    # Extract from HTML content
                    crypto_data = self._extract_crypto_from_html(data.get('content', ''))

            # Enrich with additional crypto metrics
            for symbol in self.crypto_symbols[:3]:  # Limit to prevent rate limiting
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period="1d")

                    if not hist.empty:
                        latest = hist.iloc[-1]
                        crypto_symbol = symbol.replace('-USD', '')
                        crypto_data[crypto_symbol] = {
                            'price': float(latest['Close']),
                            'volume': int(latest['Volume']),
                            'change_24h': self._calculate_24h_change(hist),
                            'high_24h': float(latest['High']),
                            'low_24h': float(latest['Low']),
                            'market_cap_rank': self._get_crypto_rank(crypto_symbol)
                        }
                except Exception as e:
                    self.logger.warning(f"Failed to get crypto data for {symbol}: {e}")

            # Calculate quality score
            quality_score = self._calculate_crypto_quality(crypto_data)

            # Create intelligence data
            intelligence = IntelligenceData(
                spider_id=self.spider_id,
                source_url=target.url,
                data_type="crypto_data",
                content=crypto_data,
                metadata={
                    'crypto_count': len(crypto_data),
                    'data_source': 'crypto_exchange',
                    'data_freshness': 'real_time'
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['crypto', 'blockchain', 'digital_assets', 'real_time'],
                target_agents=['crypto_trading_agent', 'defi_analysis_agent'],
                target_advisors=['crypto_expert', 'tech_architect']
            )

            return intelligence

        except Exception as e:
            self.logger.error(f"Error processing crypto data: {e}")
            return None

    async def _process_market_data(self, data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process market data from Polygon.io or similar sources"""
        try:
            market_data = {}

            # Process market data API response
            if 'results' in data:
                for result in data['results'][:10]:  # Limit results
                    symbol = result.get('T', 'UNKNOWN')
                    market_data[symbol] = {
                        'price': result.get('c'),  # Close price
                        'volume': result.get('v'),  # Volume
                        'high': result.get('h'),   # High
                        'low': result.get('l'),    # Low
                        'open': result.get('o'),   # Open
                        'timestamp': result.get('t'),  # Timestamp
                        'number_of_trades': result.get('n'),  # Number of trades
                        'vwap': result.get('vw')   # Volume weighted average price
                    }

            # Calculate market indicators
            market_indicators = self._calculate_market_indicators(market_data)

            # Combine market data with indicators
            processed_data = {
                'market_data': market_data,
                'market_indicators': market_indicators,
                'market_summary': self._generate_market_summary(market_data, market_indicators)
            }

            # Calculate quality score
            quality_score = self._calculate_market_indicators_quality(processed_data)

            # Create intelligence data
            intelligence = IntelligenceData(
                spider_id=self.spider_id,
                source_url=target.url,
                data_type="market_indicators",
                content=processed_data,
                metadata={
                    'symbols_analyzed': len(market_data),
                    'indicators_calculated': len(market_indicators),
                    'data_source': 'polygon_io',
                    'data_freshness': 'real_time'
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['market_data', 'indicators', 'technical_analysis', 'real_time'],
                target_agents=['technical_analysis_agent', 'algorithmic_trading_agent'],
                target_advisors=['options_master', 'ray_dalio']
            )

            return intelligence

        except Exception as e:
            self.logger.error(f"Error processing market data: {e}")
            return None

    async def _process_general_financial(self, data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process general financial data"""
        try:
            # Generic financial data processing
            financial_data = data.copy() if isinstance(data, dict) else {'raw_data': data}

            # Add timestamp if not present
            if 'timestamp' not in financial_data:
                financial_data['timestamp'] = datetime.now(timezone.utc).isoformat()

            # Extract financial keywords and metrics
            keywords = self._extract_financial_keywords(financial_data)
            financial_data['extracted_keywords'] = keywords

            # Calculate quality score
            quality_score = self.calculate_data_quality(financial_data)

            # Create intelligence data
            intelligence = IntelligenceData(
                spider_id=self.spider_id,
                source_url=target.url,
                data_type="general_financial",
                content=financial_data,
                metadata={
                    'keywords_count': len(keywords),
                    'data_source': 'general_financial',
                    'processing_method': 'generic'
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['financial', 'general'] + keywords[:5],
                target_agents=['financial_analysis_agent'],
                target_advisors=['financial_strategist']
            )

            return intelligence

        except Exception as e:
            self.logger.error(f"Error processing general financial data: {e}")
            return None

    def _extract_filing_type(self, soup: BeautifulSoup) -> str:
        """Extract SEC filing type from HTML"""
        try:
            # Look for common filing type indicators
            for tag in soup.find_all(['title', 'h1', 'h2']):
                text = tag.get_text().upper()
                if any(filing in text for filing in ['10-K', '10-Q', '8-K', 'DEF 14A', '13F']):
                    return re.search(r'(10-K|10-Q|8-K|DEF 14A|13F)', text).group(1)
            return 'UNKNOWN'
        except:
            return 'UNKNOWN'

    def _extract_company_name(self, soup: BeautifulSoup) -> str:
        """Extract company name from SEC filing"""
        try:
            # Look for company name in various locations
            for selector in [
                'span[data-tag="dei:EntityRegistrantName"]',
                '.companyName',
                'h2:contains("COMPANY")',
                'title'
            ]:
                element = soup.select_one(selector)
                if element:
                    return element.get_text().strip()
            return 'UNKNOWN'
        except:
            return 'UNKNOWN'

    def _extract_ticker_symbol(self, soup: BeautifulSoup) -> str:
        """Extract ticker symbol from SEC filing"""
        try:
            # Look for ticker in various formats
            text = soup.get_text()
            ticker_match = re.search(r'Trading Symbol[:\s]+([A-Z]{1,5})', text, re.IGNORECASE)
            if ticker_match:
                return ticker_match.group(1)

            # Alternative patterns
            for pattern in [r'NYSE:\s*([A-Z]+)', r'NASDAQ:\s*([A-Z]+)', r'\(([A-Z]{1,5})\)']:
                match = re.search(pattern, text)
                if match:
                    return match.group(1)

            return 'UNKNOWN'
        except:
            return 'UNKNOWN'

    def _extract_filing_date(self, soup: BeautifulSoup) -> str:
        """Extract filing date from SEC document"""
        try:
            date_element = soup.select_one('span[data-tag="dei:DocumentPeriodEndDate"]')
            if date_element:
                return date_element.get_text().strip()

            # Look for date patterns in text
            text = soup.get_text()
            date_match = re.search(r'Filing Date[:\s]+(\d{4}-\d{2}-\d{2})', text, re.IGNORECASE)
            if date_match:
                return date_match.group(1)

            return datetime.now().strftime('%Y-%m-%d')
        except:
            return datetime.now().strftime('%Y-%m-%d')

    def _extract_period_end(self, soup: BeautifulSoup) -> str:
        """Extract period end date from SEC filing"""
        try:
            period_element = soup.select_one('span[data-tag="dei:DocumentPeriodEndDate"]')
            if period_element:
                return period_element.get_text().strip()
            return self._extract_filing_date(soup)  # Fallback
        except:
            return datetime.now().strftime('%Y-%m-%d')

    def _extract_financial_metrics(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract key financial metrics from SEC filing"""
        metrics = {}
        try:
            text = soup.get_text()

            # Revenue patterns
            revenue_patterns = [
                r'Total Revenue[:\s\$,]*(\d+(?:,\d{3})*(?:\.\d+)?)',
                r'Net Sales[:\s\$,]*(\d+(?:,\d{3})*(?:\.\d+)?)',
                r'Total Net Revenues[:\s\$,]*(\d+(?:,\d{3})*(?:\.\d+)?)'
            ]

            for pattern in revenue_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    metrics['revenue'] = match.group(1).replace(',', '')
                    break

            # Net income patterns
            income_patterns = [
                r'Net Income[:\s\$,]*(\d+(?:,\d{3})*(?:\.\d+)?)',
                r'Net Earnings[:\s\$,]*(\d+(?:,\d{3})*(?:\.\d+)?)'
            ]

            for pattern in income_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    metrics['net_income'] = match.group(1).replace(',', '')
                    break

            # EPS patterns
            eps_match = re.search(r'Earnings per share[:\s\$,]*(\d+\.\d+)', text, re.IGNORECASE)
            if eps_match:
                metrics['eps'] = eps_match.group(1)

        except Exception as e:
            self.logger.warning(f"Error extracting financial metrics: {e}")

        return metrics

    def _extract_md_a(self, soup: BeautifulSoup) -> str:
        """Extract Management Discussion and Analysis section"""
        try:
            # Look for MD&A section
            for heading in soup.find_all(['h1', 'h2', 'h3', 'h4']):
                if 'management' in heading.get_text().lower() and 'discussion' in heading.get_text().lower():
                    # Get the next few paragraphs
                    paragraphs = []
                    for sibling in heading.find_next_siblings(['p', 'div'])[:5]:
                        paragraphs.append(sibling.get_text().strip())
                    return ' '.join(paragraphs)[:1000]  # Limit to 1000 chars
            return ''
        except:
            return ''

    def _extract_risk_factors(self, soup: BeautifulSoup) -> List[str]:
        """Extract risk factors from SEC filing"""
        try:
            risk_factors = []
            for heading in soup.find_all(['h1', 'h2', 'h3', 'h4']):
                if 'risk factors' in heading.get_text().lower():
                    # Get risk items
                    for sibling in heading.find_next_siblings(['li', 'p'])[:10]:
                        risk_text = sibling.get_text().strip()
                        if len(risk_text) > 50:  # Filter out short items
                            risk_factors.append(risk_text[:200])  # Limit length
            return risk_factors
        except:
            return []

    def _calculate_sec_quality(self, filing_info: Dict[str, Any]) -> float:
        """Calculate quality score for SEC filing data"""
        score = 0.0

        # Check completeness
        required_fields = ['filing_type', 'company', 'ticker', 'filing_date']
        present_fields = sum(1 for field in required_fields if filing_info.get(field) != 'UNKNOWN')
        score += (present_fields / len(required_fields)) * 0.4

        # Check for financial metrics
        if filing_info.get('key_metrics'):
            score += 0.3

        # Check for MD&A content
        if filing_info.get('management_discussion'):
            score += 0.2

        # Check for risk factors
        if filing_info.get('risk_factors'):
            score += 0.1

        return min(1.0, score)

    def _extract_symbols_from_url(self, url: str) -> Optional[List[str]]:
        """Extract stock symbols from URL"""
        try:
            # Common patterns for symbols in URLs
            patterns = [
                r'/quote/([A-Z]{1,5})',
                r'symbol=([A-Z]{1,5})',
                r'ticker=([A-Z]{1,5})'
            ]

            for pattern in patterns:
                matches = re.findall(pattern, url.upper())
                if matches:
                    return matches

            return None
        except:
            return None

    def _calculate_market_data_quality(self, market_data: Dict[str, Any]) -> float:
        """Calculate quality score for market data"""
        if not market_data:
            return 0.0

        total_score = 0.0
        symbol_count = 0

        for symbol, data in market_data.items():
            symbol_score = 0.0

            # Check for required fields
            required_fields = ['price', 'volume']
            present_fields = sum(1 for field in required_fields if data.get(field) is not None)
            symbol_score += (present_fields / len(required_fields)) * 0.5

            # Check for additional metrics
            optional_fields = ['pe_ratio', 'market_cap', 'beta']
            present_optional = sum(1 for field in optional_fields if data.get(field) is not None)
            symbol_score += (present_optional / len(optional_fields)) * 0.3

            # Data freshness (assume real-time = high score)
            symbol_score += 0.2

            total_score += symbol_score
            symbol_count += 1

        return total_score / symbol_count if symbol_count > 0 else 0.0

    def _extract_crypto_from_html(self, html_content: str) -> Dict[str, Any]:
        """Extract crypto data from HTML content"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            crypto_data = {}

            # Look for price elements with common CSS selectors
            price_selectors = ['.price', '.value', '[data-price]', '.quote-price']

            for selector in price_selectors:
                elements = soup.select(selector)
                for element in elements:
                    price_text = element.get_text().strip()
                    price_match = re.search(r'\$?([\d,]+\.?\d*)', price_text)
                    if price_match:
                        price = float(price_match.group(1).replace(',', ''))
                        # Try to identify the crypto symbol
                        symbol = self._identify_crypto_symbol(element)
                        if symbol:
                            crypto_data[symbol] = {'price': price}

            return crypto_data
        except:
            return {}

    def _identify_crypto_symbol(self, element) -> Optional[str]:
        """Identify crypto symbol from HTML element context"""
        try:
            # Look in element text, attributes, and nearby elements
            context_text = element.get_text() + ' ' + str(element.get('class', ''))

            # Check parent and sibling elements
            parent = element.parent
            if parent:
                context_text += ' ' + parent.get_text()

            # Common crypto symbols
            crypto_symbols = ['BTC', 'ETH', 'ADA', 'DOT', 'LINK', 'SOL', 'AVAX', 'MATIC']

            for symbol in crypto_symbols:
                if symbol in context_text.upper():
                    return symbol

            return None
        except:
            return None

    def _calculate_24h_change(self, hist_data) -> float:
        """Calculate 24-hour price change"""
        try:
            if len(hist_data) >= 2:
                current = hist_data.iloc[-1]['Close']
                previous = hist_data.iloc[-2]['Close']
                return ((current - previous) / previous) * 100
            return 0.0
        except:
            return 0.0

    def _get_crypto_rank(self, symbol: str) -> int:
        """Get crypto market cap rank (simplified)"""
        # Simplified ranking based on symbol
        rank_map = {
            'BTC': 1, 'ETH': 2, 'BNB': 3, 'ADA': 4, 'SOL': 5,
            'DOT': 6, 'AVAX': 7, 'LINK': 8, 'MATIC': 9, 'ALGO': 10
        }
        return rank_map.get(symbol.upper(), 100)

    def _calculate_crypto_quality(self, crypto_data: Dict[str, Any]) -> float:
        """Calculate quality score for crypto data"""
        if not crypto_data:
            return 0.0

        score = 0.0
        crypto_count = len(crypto_data)

        if crypto_count > 0:
            score += min(1.0, crypto_count / 5) * 0.5  # Up to 5 cryptos = full score

        # Check data completeness
        complete_entries = sum(
            1 for data in crypto_data.values()
            if isinstance(data, dict) and 'price' in data
        )

        if crypto_count > 0:
            score += (complete_entries / crypto_count) * 0.5

        return score

    def _calculate_market_indicators(self, market_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate market indicators from market data"""
        indicators = {}

        try:
            if not market_data:
                return indicators

            # Calculate average volume
            volumes = [data.get('volume', 0) for data in market_data.values() if data.get('volume')]
            if volumes:
                indicators['avg_volume'] = sum(volumes) / len(volumes)

            # Calculate price momentum (simplified)
            prices = [data.get('price', 0) for data in market_data.values() if data.get('price')]
            if prices:
                indicators['avg_price'] = sum(prices) / len(prices)
                indicators['price_range'] = max(prices) - min(prices) if len(prices) > 1 else 0

            # Calculate volatility indicator (simplified using high-low range)
            volatilities = []
            for data in market_data.values():
                if data.get('high') and data.get('low') and data.get('price'):
                    vol = ((data['high'] - data['low']) / data['price']) * 100
                    volatilities.append(vol)

            if volatilities:
                indicators['avg_volatility'] = sum(volatilities) / len(volatilities)

            # Market breadth (percentage of positive movers)
            positive_movers = sum(
                1 for data in market_data.values()
                if data.get('open') and data.get('price') and data['price'] > data['open']
            )

            if market_data:
                indicators['market_breadth'] = (positive_movers / len(market_data)) * 100

        except Exception as e:
            self.logger.warning(f"Error calculating market indicators: {e}")

        return indicators

    def _generate_market_summary(self, market_data: Dict[str, Any], indicators: Dict[str, float]) -> str:
        """Generate a summary of market conditions"""
        try:
            summary_parts = []

            if indicators.get('market_breadth'):
                breadth = indicators['market_breadth']
                if breadth > 60:
                    summary_parts.append("Strong bullish breadth")
                elif breadth > 40:
                    summary_parts.append("Neutral market breadth")
                else:
                    summary_parts.append("Weak market breadth")

            if indicators.get('avg_volatility'):
                vol = indicators['avg_volatility']
                if vol > 3:
                    summary_parts.append("High volatility environment")
                elif vol > 1.5:
                    summary_parts.append("Moderate volatility")
                else:
                    summary_parts.append("Low volatility environment")

            if indicators.get('avg_volume'):
                summary_parts.append(f"Average volume: {indicators['avg_volume']:,.0f}")

            return ". ".join(summary_parts) if summary_parts else "Market data processed successfully"

        except:
            return "Market summary unavailable"

    def _calculate_market_indicators_quality(self, processed_data: Dict[str, Any]) -> float:
        """Calculate quality score for market indicators"""
        score = 0.0

        # Market data quality
        market_data = processed_data.get('market_data', {})
        if market_data:
            score += 0.4

        # Indicators calculated
        indicators = processed_data.get('market_indicators', {})
        if indicators:
            score += 0.4 * (len(indicators) / 5)  # Up to 5 indicators

        # Summary generated
        summary = processed_data.get('market_summary', '')
        if summary and len(summary) > 10:
            score += 0.2

        return min(1.0, score)

    def _extract_financial_keywords(self, data: Dict[str, Any]) -> List[str]:
        """Extract financial keywords from data"""
        financial_keywords = [
            'revenue', 'profit', 'earnings', 'ebitda', 'cash_flow', 'debt',
            'equity', 'valuation', 'growth', 'margin', 'roe', 'roa', 'pe_ratio',
            'dividend', 'buyback', 'acquisition', 'merger', 'ipo', 'guidance'
        ]

        text = json.dumps(data).lower()
        found_keywords = []

        for keyword in financial_keywords:
            if keyword in text:
                found_keywords.append(keyword)

        return found_keywords

    def get_required_fields(self) -> List[str]:
        """Return required fields for financial data"""
        return self.required_financial_fields

    def get_timestamp_field(self) -> Optional[str]:
        """Return timestamp field name"""
        return 'timestamp'

    def get_relevance_keywords(self) -> List[str]:
        """Return relevance keywords for financial data"""
        return [
            'financial', 'stock', 'market', 'trading', 'investment',
            'earnings', 'revenue', 'profit', 'sec', 'filing', 'crypto'
        ]

    def validate_data_accuracy(self, data: Dict[str, Any]) -> bool:
        """Validate financial data accuracy"""
        try:
            # Check for reasonable price values
            if 'price' in data:
                price = float(data['price'])
                if price <= 0 or price > 1000000:  # Reasonable price range
                    return False

            # Check for reasonable volume values
            if 'volume' in data:
                volume = float(data['volume'])
                if volume < 0:
                    return False

            # Check for reasonable percentage values
            for field in ['change_24h', 'dividend_yield', 'beta']:
                if field in data:
                    value = float(data[field])
                    if abs(value) > 1000:  # Reasonable percentage range
                        return False

            return True

        except (ValueError, TypeError):
            return False
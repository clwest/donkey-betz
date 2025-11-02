"""
Financial Intelligence Spider Army
Massive data collection for Warren Buffett, Cathie Wood, Ray Dalio and other financial advisors
"""

import scrapy
import re
import json
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
from .base_spider import FinancialIntelligenceSpider


class StockNewsSpider(FinancialIntelligenceSpider):
    """
    Stock news and market sentiment spider
    Feeds Warren Buffett and other value investing advisors
    """

    name = 'stock_news'
    allowed_domains = ['finance.yahoo.com', 'marketwatch.com', 'bloomberg.com', 'reuters.com']

    # Target symbols for major market movers
    target_symbols = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'BRK.A', 'BRK.B',
        'JPM', 'V', 'JNJ', 'WMT', 'PG', 'UNH', 'HD', 'MA', 'DIS', 'PYPL', 'NFLX'
    ]

    def start_requests(self):
        """Generate requests for financial news"""

        # Yahoo Finance news for each symbol
        for symbol in self.target_symbols:
            url = f"https://finance.yahoo.com/quote/{symbol}/news"
            yield scrapy.Request(
                url=url,
                callback=self.parse_yahoo_news,
                meta={'symbol': symbol, 'source': 'yahoo_finance'}
            )

        # MarketWatch latest news
        yield scrapy.Request(
            url="https://www.marketwatch.com/latest-news",
            callback=self.parse_marketwatch_news,
            meta={'source': 'marketwatch'}
        )

    def parse_yahoo_news(self, response):
        """Parse Yahoo Finance news for specific stocks"""
        news_items = response.css('li[data-test-locator="StreamItem"]')

        for item in news_items:
            try:
                news_data = self.extract_yahoo_news_item(item, response)
                if news_data:
                    intelligence = self.process_item(news_data, response)
                    if intelligence:
                        yield intelligence

            except Exception as e:
                self.logger.error(f"Error extracting Yahoo news: {e}")

    def extract_yahoo_news_item(self, item, response):
        """Extract news item from Yahoo Finance"""
        try:
            headline = item.css('h3 a::text').get()
            if not headline:
                return None

            summary = item.css('p::text').get() or ""
            time_text = item.css('div[data-test-locator="TimeStamp"]::text').get() or ""
            source = item.css('div[data-test-locator="Provider"]::text').get() or ""

            article_url = item.css('h3 a::attr(href)').get()
            if article_url:
                article_url = urljoin(response.url, article_url)

            news_data = {
                'headline': headline.strip(),
                'summary': summary.strip(),
                'time_text': time_text.strip(),
                'source': source.strip(),
                'article_url': article_url,
                'symbol': response.meta.get('symbol'),
                'platform': 'yahoo_finance',
                'data_type': 'stock_news',
                'scraped_at': datetime.now().isoformat(),
                'advisor_relevance': {
                    'warren_buffett': self.calculate_buffett_relevance(headline, summary),
                    'cathie_wood': self.calculate_innovation_relevance(headline, summary),
                    'ray_dalio': self.calculate_macro_relevance(headline, summary)
                }
            }

            return news_data

        except Exception as e:
            self.logger.error(f"Error extracting Yahoo news item: {e}")
            return None

    def parse_marketwatch_news(self, response):
        """Parse MarketWatch latest news"""
        articles = response.css('div.article__content')

        for article in articles:
            try:
                news_data = self.extract_marketwatch_article(article, response)
                if news_data:
                    intelligence = self.process_item(news_data, response)
                    if intelligence:
                        yield intelligence

            except Exception as e:
                self.logger.error(f"Error extracting MarketWatch article: {e}")

    def extract_marketwatch_article(self, article, response):
        """Extract article from MarketWatch"""
        try:
            headline = article.css('h3.article__headline a::text').get()
            if not headline:
                return None

            summary = article.css('p.article__summary::text').get() or ""
            time_text = article.css('span.article__timestamp::text').get() or ""

            article_url = article.css('h3.article__headline a::attr(href)').get()
            if article_url:
                article_url = urljoin(response.url, article_url)

            news_data = {
                'headline': headline.strip(),
                'summary': summary.strip(),
                'time_text': time_text.strip(),
                'article_url': article_url,
                'platform': 'marketwatch',
                'data_type': 'market_news',
                'scraped_at': datetime.now().isoformat(),
                'advisor_relevance': {
                    'warren_buffett': self.calculate_buffett_relevance(headline, summary),
                    'ray_dalio': self.calculate_macro_relevance(headline, summary),
                    'peter_lynch': self.calculate_growth_relevance(headline, summary)
                }
            }

            return news_data

        except Exception as e:
            self.logger.error(f"Error extracting MarketWatch article: {e}")
            return None

    def calculate_buffett_relevance(self, headline, summary):
        """Calculate relevance score for Warren Buffett's investment style"""
        text = f"{headline} {summary}".lower()

        buffett_keywords = [
            'berkshire', 'value', 'dividend', 'cash flow', 'earnings', 'moat',
            'competitive advantage', 'management', 'debt', 'buyback', 'intrinsic value',
            'long term', 'quality', 'franchise', 'predictable', 'consumer goods',
            'insurance', 'railroad', 'utility', 'pricing power'
        ]

        score = sum(1 for keyword in buffett_keywords if keyword in text)
        return min(1.0, score * 0.1)

    def calculate_innovation_relevance(self, headline, summary):
        """Calculate relevance for innovation investors like Cathie Wood"""
        text = f"{headline} {summary}".lower()

        innovation_keywords = [
            'ai', 'artificial intelligence', 'machine learning', 'automation',
            'genomics', 'crispr', 'blockchain', 'cryptocurrency', 'tesla',
            'electric vehicle', 'autonomous', 'robotics', 'space', 'satellite',
            'cloud computing', 'digital transformation', 'innovation', 'disruptive',
            'breakthrough', 'next generation', 'future', 'renewable energy'
        ]

        score = sum(1 for keyword in innovation_keywords if keyword in text)
        return min(1.0, score * 0.08)

    def calculate_macro_relevance(self, headline, summary):
        """Calculate relevance for macro investors like Ray Dalio"""
        text = f"{headline} {summary}".lower()

        macro_keywords = [
            'federal reserve', 'interest rate', 'inflation', 'gdp', 'unemployment',
            'monetary policy', 'fiscal policy', 'debt cycle', 'currency',
            'geopolitical', 'trade war', 'recession', 'economic data',
            'central bank', 'yield curve', 'commodities', 'dollar', 'china',
            'global economy', 'emerging markets'
        ]

        score = sum(1 for keyword in macro_keywords if keyword in text)
        return min(1.0, score * 0.1)

    def calculate_growth_relevance(self, headline, summary):
        """Calculate relevance for growth investors like Peter Lynch"""
        text = f"{headline} {summary}".lower()

        growth_keywords = [
            'growth', 'revenue growth', 'earnings growth', 'expansion',
            'new product', 'market share', 'consumer spending', 'retail',
            'restaurant', 'technology adoption', 'digital', 'e-commerce',
            'subscription', 'recurring revenue', 'user growth', 'mobile',
            'demographic trend', 'millennial', 'gen z'
        ]

        score = sum(1 for keyword in growth_keywords if keyword in text)
        return min(1.0, score * 0.09)


class CryptoIntelligenceSpider(FinancialIntelligenceSpider):
    """
    Cryptocurrency market intelligence spider
    """

    name = 'crypto_intelligence'
    allowed_domains = ['coindesk.com', 'cointelegraph.com', 'decrypt.co']

    def start_requests(self):
        """Generate requests for crypto news and data"""
        crypto_sources = [
            "https://www.coindesk.com/markets/",
            "https://cointelegraph.com/category/market-analysis",
            "https://decrypt.co/news/crypto"
        ]

        for url in crypto_sources:
            yield scrapy.Request(
                url=url,
                callback=self.parse_crypto_news,
                meta={'source': urlparse(url).netloc}
            )

    def parse_crypto_news(self, response):
        """Parse cryptocurrency news"""
        # Generic article selector that works across sites
        articles = response.css('article, div.article, div[class*="article"]')

        for article in articles:
            try:
                crypto_data = self.extract_crypto_article(article, response)
                if crypto_data:
                    intelligence = self.process_item(crypto_data, response)
                    if intelligence:
                        yield intelligence

            except Exception as e:
                self.logger.error(f"Error extracting crypto article: {e}")

    def extract_crypto_article(self, article, response):
        """Extract cryptocurrency article data"""
        try:
            # Try multiple selectors for headline
            headline = (
                article.css('h1::text, h2::text, h3::text').get() or
                article.css('a[class*="headline"]::text').get() or
                article.css('[class*="title"]::text').get()
            )

            if not headline or len(headline.strip()) < 10:
                return None

            # Try multiple selectors for summary/description
            summary = (
                article.css('p::text').get() or
                article.css('[class*="summary"]::text').get() or
                article.css('[class*="description"]::text').get() or
                ""
            )

            # Extract article URL
            article_url = (
                article.css('a::attr(href)').get() or
                article.css('h1 a::attr(href), h2 a::attr(href), h3 a::attr(href)').get()
            )

            if article_url:
                article_url = urljoin(response.url, article_url)

            crypto_data = {
                'headline': headline.strip(),
                'summary': summary.strip(),
                'article_url': article_url,
                'source': response.meta.get('source'),
                'platform': 'crypto_news',
                'data_type': 'cryptocurrency',
                'scraped_at': datetime.now().isoformat(),
                'crypto_relevance': self.calculate_crypto_relevance(headline, summary),
                'advisor_relevance': {
                    'cathie_wood': self.calculate_innovation_relevance(headline, summary),
                    'michael_saylor': self.calculate_bitcoin_relevance(headline, summary),
                    'ray_dalio': self.calculate_macro_relevance(headline, summary)
                }
            }

            return crypto_data

        except Exception as e:
            self.logger.error(f"Error extracting crypto article: {e}")
            return None

    def calculate_crypto_relevance(self, headline, summary):
        """Calculate overall cryptocurrency relevance"""
        text = f"{headline} {summary}".lower()

        crypto_keywords = [
            'bitcoin', 'ethereum', 'cryptocurrency', 'crypto', 'blockchain',
            'defi', 'nft', 'smart contract', 'altcoin', 'stablecoin',
            'mining', 'wallet', 'exchange', 'trading', 'hodl',
            'bull market', 'bear market', 'price prediction', 'adoption'
        ]

        score = sum(1 for keyword in crypto_keywords if keyword in text)
        return min(1.0, score * 0.1)

    def calculate_bitcoin_relevance(self, headline, summary):
        """Calculate Bitcoin-specific relevance for Michael Saylor style investors"""
        text = f"{headline} {summary}".lower()

        bitcoin_keywords = [
            'bitcoin', 'btc', 'digital gold', 'store of value', 'inflation hedge',
            'institutional adoption', 'corporate treasury', 'microstrategy',
            'el salvador', 'legal tender', 'mining', 'hashrate', 'halving'
        ]

        score = sum(1 for keyword in bitcoin_keywords if keyword in text)
        return min(1.0, score * 0.12)


class MarketDataSpider(FinancialIntelligenceSpider):
    """
    Real-time market data spider for trading agents
    """

    name = 'market_data'
    allowed_domains = ['finance.yahoo.com']

    # Major market indices and ETFs
    market_symbols = [
        'SPY', 'QQQ', 'IWM', 'VTI', 'GLD', 'TLT', 'VIX',
        '^GSPC', '^IXIC', '^DJI', '^RUT', '^TNX'
    ]

    def start_requests(self):
        """Generate requests for market data"""
        for symbol in self.market_symbols:
            url = f"https://finance.yahoo.com/quote/{symbol}"
            yield scrapy.Request(
                url=url,
                callback=self.parse_market_data,
                meta={'symbol': symbol}
            )

    def parse_market_data(self, response):
        """Parse market data from Yahoo Finance"""
        try:
            market_data = self.extract_market_data(response)
            if market_data:
                intelligence = self.process_item(market_data, response)
                if intelligence:
                    yield intelligence

        except Exception as e:
            self.logger.error(f"Error extracting market data: {e}")

    def extract_market_data(self, response):
        """Extract market data from Yahoo Finance quote page"""
        try:
            symbol = response.meta.get('symbol')

            # Extract current price
            current_price = response.css('[data-symbol="' + symbol + '"] [data-field="regularMarketPrice"]::text').get()

            # Extract change and change percent
            change = response.css('[data-field="regularMarketChange"]::text').get()
            change_percent = response.css('[data-field="regularMarketChangePercent"]::text').get()

            # Extract volume
            volume = response.css('[data-field="regularMarketVolume"]::text').get()

            # Extract market cap if available
            market_cap = response.css('[data-field="marketCap"]::text').get()

            market_data = {
                'symbol': symbol,
                'current_price': current_price,
                'change': change,
                'change_percent': change_percent,
                'volume': volume,
                'market_cap': market_cap,
                'timestamp': datetime.now().isoformat(),
                'platform': 'yahoo_finance',
                'data_type': 'market_data',
                'scraped_at': datetime.now().isoformat()
            }

            return market_data

        except Exception as e:
            self.logger.error(f"Error extracting market data: {e}")
            return None


class SECFilingsSpider(FinancialIntelligenceSpider):
    """
    SEC filings spider for fundamental analysis
    Perfect for Warren Buffett style deep value analysis
    """

    name = 'sec_filings'
    allowed_domains = ['sec.gov']

    # Target major companies for filings monitoring
    target_companies = [
        '0000320193',  # Apple
        '0000789019',  # Microsoft
        '0000051143',  # IBM
        '0000001652',  # Berkshire Hathaway
        '0000018230',  # AT&T
        '0000019617',  # JPMorgan Chase
    ]

    def start_requests(self):
        """Generate requests for SEC filings"""
        for cik in self.target_companies:
            url = f"https://www.sec.gov/cgi-bin/browse-edgar?CIK={cik}&Find=Search&owner=exclude&action=getcompany"
            yield scrapy.Request(
                url=url,
                callback=self.parse_company_filings,
                meta={'cik': cik}
            )

    def parse_company_filings(self, response):
        """Parse SEC company filings page"""
        filing_rows = response.css('table.tableFile2 tr')[1:]  # Skip header

        for row in filing_rows[:10]:  # Latest 10 filings
            try:
                filing_data = self.extract_filing_data(row, response)
                if filing_data:
                    intelligence = self.process_item(filing_data, response)
                    if intelligence:
                        yield intelligence

            except Exception as e:
                self.logger.error(f"Error extracting SEC filing: {e}")

    def extract_filing_data(self, row, response):
        """Extract filing data from SEC table row"""
        try:
            cells = row.css('td')
            if len(cells) < 5:
                return None

            filing_type = cells[0].css('::text').get()
            description = cells[2].css('::text').get()
            filing_date = cells[3].css('::text').get()

            # Get document URL
            doc_link = cells[1].css('a::attr(href)').get()
            if doc_link:
                doc_url = urljoin(response.url, doc_link)
            else:
                doc_url = None

            filing_data = {
                'cik': response.meta.get('cik'),
                'filing_type': filing_type.strip() if filing_type else "",
                'description': description.strip() if description else "",
                'filing_date': filing_date.strip() if filing_date else "",
                'document_url': doc_url,
                'platform': 'sec_edgar',
                'data_type': 'sec_filing',
                'scraped_at': datetime.now().isoformat(),
                'buffett_relevance': self.calculate_filing_relevance(filing_type, description)
            }

            return filing_data

        except Exception as e:
            self.logger.error(f"Error extracting filing data: {e}")
            return None

    def calculate_filing_relevance(self, filing_type, description):
        """Calculate relevance for fundamental analysis"""
        if not filing_type:
            return 0.0

        # Key filing types for fundamental analysis
        important_filings = {
            '10-K': 1.0,      # Annual report
            '10-Q': 0.8,      # Quarterly report
            '8-K': 0.6,       # Current report
            '13F': 0.9,       # Institutional holdings
            'DEF 14A': 0.7,   # Proxy statement
            '4': 0.5,         # Insider trading
        }

        return important_filings.get(filing_type.strip(), 0.3)
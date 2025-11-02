"""
Advisor-Specific Intelligence Spiders
Specialized spiders for feeding the 25 legendary advisor personalities
"""

import scrapy
import re
import json
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
from .base_spider import FinancialIntelligenceSpider


class BerkshireHathawaySpider(FinancialIntelligenceSpider):
    """
    Warren Buffett's Berkshire Hathaway intelligence spider
    Monitors Berkshire activities, 13F filings, and value opportunities
    """

    name = 'berkshire_intelligence'
    allowed_domains = ['berkshirehathaway.com', 'sec.gov', 'finance.yahoo.com']

    target_advisors = ['warren_buffett', 'charlie_munger']
    target_agents = ['value_investing_agent', 'berkshire_analyzer']

    def start_requests(self):
        """Generate requests for Berkshire intelligence"""
        urls = [
            'https://www.berkshirehathaway.com/news/news.html',
            'https://www.berkshirehathaway.com/letters/letters.html',
            'https://finance.yahoo.com/quote/BRK-A/holders',
            'https://finance.yahoo.com/quote/BRK-B/holders'
        ]

        for url in urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse_berkshire_page,
                meta={'page_type': self.get_page_type(url)}
            )

    def get_page_type(self, url):
        """Determine page type from URL"""
        if 'news' in url:
            return 'news'
        elif 'letters' in url:
            return 'shareholder_letters'
        elif 'holders' in url:
            return 'holdings'
        return 'general'

    def parse_berkshire_page(self, response):
        """Parse Berkshire Hathaway pages"""
        page_type = response.meta.get('page_type')

        if page_type == 'news':
            yield from self.parse_berkshire_news(response)
        elif page_type == 'shareholder_letters':
            yield from self.parse_shareholder_letters(response)
        elif page_type == 'holdings':
            yield from self.parse_holdings_data(response)

    def parse_berkshire_news(self, response):
        """Parse Berkshire news page"""
        news_items = response.css('table tr')

        for item in news_items:
            try:
                news_data = self.extract_berkshire_news(item, response)
                if news_data:
                    intelligence = self.process_item(news_data, response)
                    if intelligence:
                        yield intelligence

            except Exception as e:
                self.logger.error(f"Error extracting Berkshire news: {e}")

    def extract_berkshire_news(self, item, response):
        """Extract news item from Berkshire news table"""
        try:
            date_cell = item.css('td:first-child::text').get()
            if not date_cell:
                return None

            news_link = item.css('td a::attr(href)').get()
            news_text = item.css('td a::text').get()

            if not news_text:
                return None

            if news_link:
                news_url = urljoin(response.url, news_link)
            else:
                news_url = None

            news_data = {
                'date': date_cell.strip(),
                'headline': news_text.strip(),
                'news_url': news_url,
                'source': 'berkshire_hathaway',
                'platform': 'berkshire_official',
                'data_type': 'berkshire_news',
                'scraped_at': datetime.now().isoformat(),
                'buffett_relevance': 1.0,  # Maximum relevance - direct from Berkshire
                'analysis': self.analyze_berkshire_news(news_text)
            }

            return news_data

        except Exception as e:
            self.logger.error(f"Error extracting Berkshire news: {e}")
            return None

    def parse_shareholder_letters(self, response):
        """Parse shareholder letters page"""
        letter_links = response.css('table a[href$=".pdf"]')

        for link in letter_links:
            try:
                letter_data = self.extract_letter_data(link, response)
                if letter_data:
                    intelligence = self.process_item(letter_data, response)
                    if intelligence:
                        yield intelligence

            except Exception as e:
                self.logger.error(f"Error extracting letter data: {e}")

    def extract_letter_data(self, link, response):
        """Extract shareholder letter data"""
        try:
            letter_text = link.css('::text').get()
            letter_url = link.css('::attr(href)').get()

            if not letter_text:
                return None

            if letter_url:
                letter_url = urljoin(response.url, letter_url)

            # Extract year from text or URL
            year_match = re.search(r'(\d{4})', letter_text)
            year = year_match.group(1) if year_match else ''

            letter_data = {
                'title': letter_text.strip(),
                'year': year,
                'letter_url': letter_url,
                'source': 'berkshire_hathaway',
                'platform': 'berkshire_official',
                'data_type': 'shareholder_letter',
                'scraped_at': datetime.now().isoformat(),
                'buffett_relevance': 1.0
            }

            return letter_data

        except Exception as e:
            self.logger.error(f"Error extracting letter data: {e}")
            return None

    def parse_holdings_data(self, response):
        """Parse Berkshire holdings data from Yahoo Finance"""
        holdings_table = response.css('table tbody tr')

        for row in holdings_table:
            try:
                holding_data = self.extract_holding_data(row, response)
                if holding_data:
                    intelligence = self.process_item(holding_data, response)
                    if intelligence:
                        yield intelligence

            except Exception as e:
                self.logger.error(f"Error extracting holding data: {e}")

    def extract_holding_data(self, row, response):
        """Extract individual holding data"""
        try:
            cells = row.css('td')
            if len(cells) < 3:
                return None

            symbol = cells[0].css('::text').get()
            shares = cells[1].css('::text').get()
            value = cells[2].css('::text').get()

            holding_data = {
                'symbol': symbol.strip() if symbol else '',
                'shares': shares.strip() if shares else '',
                'value': value.strip() if value else '',
                'source': 'yahoo_finance',
                'berkshire_class': 'BRK-A' if 'BRK-A' in response.url else 'BRK-B',
                'platform': 'yahoo_finance',
                'data_type': 'berkshire_holding',
                'scraped_at': datetime.now().isoformat(),
                'buffett_relevance': 0.9
            }

            return holding_data

        except Exception as e:
            self.logger.error(f"Error extracting holding data: {e}")
            return None

    def analyze_berkshire_news(self, news_text):
        """Analyze Berkshire news for key themes"""
        text_lower = news_text.lower()

        themes = {
            'acquisition': bool(re.search(r'\b(acquire|acquisition|purchase|buy)\b', text_lower)),
            'earnings': bool(re.search(r'\b(earnings|profit|income|results)\b', text_lower)),
            'investment': bool(re.search(r'\b(investment|invest|stake|position)\b', text_lower)),
            'annual_meeting': bool(re.search(r'\b(annual meeting|shareholder meeting|woodstock)\b', text_lower)),
            'dividend': bool(re.search(r'\b(dividend|payout|distribution)\b', text_lower)),
            'share_repurchase': bool(re.search(r'\b(buyback|repurchase|shares)\b', text_lower))
        }

        return themes


class CathieWoodInnovationSpider(FinancialIntelligenceSpider):
    """
    Cathie Wood / ARK Invest innovation intelligence spider
    Monitors disruptive innovation trends and ARK trading activity
    """

    name = 'cathie_wood_innovation'
    allowed_domains = ['ark-invest.com', 'cathiewood.com']

    target_advisors = ['cathie_wood', 'marc_andreessen', 'peter_thiel']
    target_agents = ['innovation_scout', 'disruptive_tech_analyzer', 'ark_tracker']

    innovation_keywords = [
        'artificial intelligence', 'machine learning', 'autonomous vehicles',
        'genomics', 'crispr', 'gene therapy', 'blockchain', 'cryptocurrency',
        'space exploration', 'robotics', 'energy storage', 'fintech'
    ]

    def start_requests(self):
        """Generate requests for innovation intelligence"""
        urls = [
            'https://ark-invest.com/articles/',
            'https://ark-invest.com/research/',
            'https://ark-invest.com/active-etfs/'
        ]

        for url in urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse_ark_page,
                meta={'page_type': self.get_ark_page_type(url)}
            )

    def get_ark_page_type(self, url):
        """Determine ARK page type"""
        if 'articles' in url:
            return 'articles'
        elif 'research' in url:
            return 'research'
        elif 'etfs' in url:
            return 'etfs'
        return 'general'

    def parse_ark_page(self, response):
        """Parse ARK Invest pages"""
        page_type = response.meta.get('page_type')

        if page_type == 'articles':
            yield from self.parse_ark_articles(response)
        elif page_type == 'research':
            yield from self.parse_ark_research(response)
        elif page_type == 'etfs':
            yield from self.parse_ark_etfs(response)

    def parse_ark_articles(self, response):
        """Parse ARK articles page"""
        article_cards = response.css('.article-card, .post-card, article')

        for card in article_cards:
            try:
                article_data = self.extract_ark_article(card, response)
                if article_data:
                    intelligence = self.process_item(article_data, response)
                    if intelligence:
                        yield intelligence

            except Exception as e:
                self.logger.error(f"Error extracting ARK article: {e}")

    def extract_ark_article(self, card, response):
        """Extract ARK article data"""
        try:
            title = card.css('h1::text, h2::text, h3::text').get()
            if not title:
                return None

            summary = card.css('p::text').get() or ""
            date = card.css('.date::text, time::text').get() or ""

            article_url = card.css('a::attr(href)').get()
            if article_url:
                article_url = urljoin(response.url, article_url)

            article_data = {
                'title': title.strip(),
                'summary': summary.strip(),
                'date': date.strip(),
                'article_url': article_url,
                'source': 'ark_invest',
                'platform': 'ark_official',
                'data_type': 'innovation_research',
                'scraped_at': datetime.now().isoformat(),
                'cathie_wood_relevance': 1.0,
                'innovation_analysis': self.analyze_innovation_content(title, summary),
                'disruptive_score': self.calculate_disruptive_score(title, summary)
            }

            return article_data

        except Exception as e:
            self.logger.error(f"Error extracting ARK article: {e}")
            return None

    def analyze_innovation_content(self, title, summary):
        """Analyze content for innovation themes"""
        text = f"{title} {summary}".lower()

        innovation_themes = {}
        for keyword in self.innovation_keywords:
            innovation_themes[keyword.replace(' ', '_')] = keyword in text

        return innovation_themes

    def calculate_disruptive_score(self, title, summary):
        """Calculate disruptive innovation score"""
        text = f"{title} {summary}".lower()

        disruptive_indicators = [
            'disruption', 'revolutionary', 'breakthrough', 'transformative',
            'paradigm shift', 'game changer', 'exponential growth',
            'next generation', 'cutting edge', 'pioneering'
        ]

        score = sum(1 for indicator in disruptive_indicators if indicator in text)
        innovation_keyword_score = sum(1 for keyword in self.innovation_keywords if keyword in text)

        total_score = (score * 0.1) + (innovation_keyword_score * 0.15)
        return min(1.0, total_score)


class RayDalioMacroSpider(FinancialIntelligenceSpider):
    """
    Ray Dalio macro economic intelligence spider
    Monitors global economic trends, central bank policies, and debt cycles
    """

    name = 'ray_dalio_macro'
    allowed_domains = ['principles.com', 'bridgewater.com', 'federalreserve.gov', 'ecb.europa.eu']

    target_advisors = ['ray_dalio', 'paul_tudor_jones', 'stanley_druckenmiller']
    target_agents = ['macro_analyst', 'currency_trader', 'economic_cycle_tracker']

    def start_requests(self):
        """Generate requests for macro economic intelligence"""
        urls = [
            'https://www.federalreserve.gov/newsevents/pressreleases.htm',
            'https://www.principles.com/big-debt-cycles/',
            'https://www.principles.com/the-economy/'
        ]

        for url in urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse_macro_page,
                meta={'source': urlparse(url).netloc}
            )

    def parse_macro_page(self, response):
        """Parse macro economic pages"""
        source = response.meta.get('source')

        if 'federalreserve.gov' in source:
            yield from self.parse_fed_releases(response)
        elif 'principles.com' in source:
            yield from self.parse_principles_content(response)

    def parse_fed_releases(self, response):
        """Parse Federal Reserve press releases"""
        release_items = response.css('.row-item, .press-release-item')

        for item in release_items:
            try:
                release_data = self.extract_fed_release(item, response)
                if release_data:
                    intelligence = self.process_item(release_data, response)
                    if intelligence:
                        yield intelligence

            except Exception as e:
                self.logger.error(f"Error extracting Fed release: {e}")

    def extract_fed_release(self, item, response):
        """Extract Federal Reserve release data"""
        try:
            title = item.css('a::text').get()
            if not title:
                return None

            date = item.css('.date::text, time::text').get() or ""
            release_url = item.css('a::attr(href)').get()

            if release_url:
                release_url = urljoin(response.url, release_url)

            release_data = {
                'title': title.strip(),
                'date': date.strip(),
                'release_url': release_url,
                'source': 'federal_reserve',
                'platform': 'fed_official',
                'data_type': 'central_bank_communication',
                'scraped_at': datetime.now().isoformat(),
                'ray_dalio_relevance': self.calculate_macro_relevance(title),
                'policy_impact': self.analyze_policy_impact(title)
            }

            return release_data

        except Exception as e:
            self.logger.error(f"Error extracting Fed release: {e}")
            return None

    def calculate_macro_relevance(self, title):
        """Calculate macro relevance for Ray Dalio style analysis"""
        title_lower = title.lower()

        macro_keywords = [
            'interest rate', 'monetary policy', 'inflation', 'employment',
            'economic outlook', 'financial stability', 'balance sheet',
            'quantitative easing', 'federal funds rate', 'yield curve'
        ]

        matches = sum(1 for keyword in macro_keywords if keyword in title_lower)
        return min(1.0, matches * 0.2)

    def analyze_policy_impact(self, title):
        """Analyze potential policy impact"""
        title_lower = title.lower()

        impact_indicators = {
            'rate_decision': 'rate' in title_lower and ('increase' in title_lower or 'decrease' in title_lower),
            'inflation_focus': 'inflation' in title_lower,
            'employment_focus': 'employment' in title_lower or 'job' in title_lower,
            'financial_stability': 'stability' in title_lower or 'risk' in title_lower,
            'emergency_action': 'emergency' in title_lower or 'urgent' in title_lower
        }

        return impact_indicators


class PeterThielStartupSpider(FinancialIntelligenceSpider):
    """
    Peter Thiel startup and monopoly intelligence spider
    Monitors Y Combinator, startup funding, and monopoly businesses
    """

    name = 'peter_thiel_startups'
    allowed_domains = ['ycombinator.com', 'crunchbase.com', 'techcrunch.com']

    target_advisors = ['peter_thiel', 'paul_graham', 'marc_andreessen']
    target_agents = ['startup_analyzer', 'venture_scout', 'monopoly_identifier']

    def start_requests(self):
        """Generate requests for startup intelligence"""
        urls = [
            'https://www.ycombinator.com/companies',
            'https://techcrunch.com/category/startups/',
            'https://news.ycombinator.com/'
        ]

        for url in urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse_startup_page,
                meta={'source': urlparse(url).netloc}
            )

    def parse_startup_page(self, response):
        """Parse startup ecosystem pages"""
        source = response.meta.get('source')

        if 'ycombinator.com' in source:
            yield from self.parse_yc_companies(response)
        elif 'techcrunch.com' in source:
            yield from self.parse_techcrunch_startups(response)
        elif 'news.ycombinator.com' in source:
            yield from self.parse_hacker_news(response)

    def parse_yc_companies(self, response):
        """Parse Y Combinator companies"""
        company_cards = response.css('.company-card, .startup-card')

        for card in company_cards:
            try:
                company_data = self.extract_yc_company(card, response)
                if company_data:
                    intelligence = self.process_item(company_data, response)
                    if intelligence:
                        yield intelligence

            except Exception as e:
                self.logger.error(f"Error extracting YC company: {e}")

    def extract_yc_company(self, card, response):
        """Extract Y Combinator company data"""
        try:
            name = card.css('h3::text, .company-name::text').get()
            if not name:
                return None

            description = card.css('p::text, .description::text').get() or ""
            batch = card.css('.batch::text, .year::text').get() or ""

            company_url = card.css('a::attr(href)').get()
            if company_url and not company_url.startswith('http'):
                company_url = urljoin(response.url, company_url)

            company_data = {
                'name': name.strip(),
                'description': description.strip(),
                'batch': batch.strip(),
                'company_url': company_url,
                'source': 'y_combinator',
                'platform': 'yc_official',
                'data_type': 'startup_profile',
                'scraped_at': datetime.now().isoformat(),
                'thiel_relevance': self.calculate_thiel_relevance(description),
                'monopoly_potential': self.analyze_monopoly_potential(description),
                'contrarian_score': self.calculate_contrarian_score(description)
            }

            return company_data

        except Exception as e:
            self.logger.error(f"Error extracting YC company: {e}")
            return None

    def calculate_thiel_relevance(self, description):
        """Calculate relevance for Peter Thiel's investment philosophy"""
        desc_lower = description.lower()

        thiel_concepts = [
            'monopoly', 'network effects', 'zero to one', 'vertical integration',
            'proprietary technology', 'economies of scale', 'brand power',
            'switching costs', 'regulatory advantages', 'breakthrough'
        ]

        matches = sum(1 for concept in thiel_concepts if concept in desc_lower)
        return min(1.0, matches * 0.15)

    def analyze_monopoly_potential(self, description):
        """Analyze monopoly potential using Thiel's framework"""
        desc_lower = description.lower()

        monopoly_indicators = {
            'proprietary_tech': bool(re.search(r'\b(proprietary|patent|unique technology|breakthrough)\b', desc_lower)),
            'network_effects': bool(re.search(r'\b(network|platform|marketplace|social)\b', desc_lower)),
            'economies_of_scale': bool(re.search(r'\b(scale|infrastructure|fixed costs)\b', desc_lower)),
            'branding': bool(re.search(r'\b(brand|marketing|customer loyalty)\b', desc_lower)),
            'regulatory_moat': bool(re.search(r'\b(regulation|compliance|licensed|approved)\b', desc_lower))
        }

        return monopoly_indicators

    def calculate_contrarian_score(self, description):
        """Calculate contrarian thinking score"""
        desc_lower = description.lower()

        contrarian_indicators = [
            'different approach', 'revolutionary', 'reimagining', 'rethinking',
            'first of its kind', 'never been done', 'contrary to', 'against conventional'
        ]

        score = sum(1 for indicator in contrarian_indicators if indicator in desc_lower)
        return min(1.0, score * 0.2)
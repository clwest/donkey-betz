"""
Justia Legal Information Spider (Playwright-enabled)
=====================================================

Session 403: Playwright-enabled spider for Justia legal resources.

Uses Playwright to bypass Cloudflare protection and scrape:
- Family law articles and guides
- Divorce law by state (Colorado focus)
- Custody and child support information
- Legal definitions and procedures

Source: https://www.justia.com/family/

All data is publicly accessible legal information.
"""

import asyncio
import logging
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from bs4 import BeautifulSoup

try:
    from playwright.async_api import async_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False

logger = logging.getLogger(__name__)


class JustiaPlaywrightSpider:
    """Playwright-enabled spider for Justia legal resources"""

    name = "justia_family_law"
    base_url = "https://www.justia.com"

    # Family law topics to scrape
    FAMILY_LAW_URLS = [
        # Main family law pages
        {
            'url': '/family/',
            'category': 'Family Law Overview',
            'tags': ['family_law', 'overview'],
        },
        # Divorce
        {
            'url': '/family/divorce/',
            'category': 'Divorce',
            'tags': ['divorce', 'family_law', 'dissolution'],
        },
        {
            'url': '/family/divorce/grounds-for-divorce/',
            'category': 'Grounds for Divorce',
            'tags': ['divorce', 'grounds', 'family_law'],
        },
        {
            'url': '/family/divorce/divorce-process/',
            'category': 'Divorce Process',
            'tags': ['divorce', 'process', 'procedure', 'family_law'],
        },
        # Child Custody
        {
            'url': '/family/child-custody/',
            'category': 'Child Custody',
            'tags': ['custody', 'children', 'family_law'],
        },
        {
            'url': '/family/child-custody/types-of-custody/',
            'category': 'Types of Custody',
            'tags': ['custody', 'legal_custody', 'physical_custody', 'family_law'],
        },
        {
            'url': '/family/child-custody/custody-modification/',
            'category': 'Custody Modification',
            'tags': ['custody', 'modification', 'change', 'family_law'],
        },
        # Child Support
        {
            'url': '/family/child-support/',
            'category': 'Child Support',
            'tags': ['child_support', 'support', 'family_law'],
        },
        {
            'url': '/family/child-support/child-support-guidelines/',
            'category': 'Child Support Guidelines',
            'tags': ['child_support', 'guidelines', 'calculation', 'family_law'],
        },
        # Parenting
        {
            'url': '/family/parenting-time-visitation/',
            'category': 'Parenting Time & Visitation',
            'tags': ['parenting_time', 'visitation', 'custody', 'family_law'],
        },
        # Colorado-specific (if available)
        {
            'url': '/lawyers/family-law/colorado/',
            'category': 'Colorado Family Law',
            'tags': ['colorado', 'family_law', 'state_specific'],
        },
    ]

    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None

    async def start_browser(self):
        """Initialize Playwright browser with anti-detection measures"""
        if not HAS_PLAYWRIGHT:
            logger.error("Playwright not installed. Run: pip install playwright && playwright install chromium")
            return False

        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                ]
            )

            # Create context with anti-detection
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale='en-US',
                timezone_id='America/Denver',  # Colorado timezone
            )

            # Anti-detection scripts
            await self.context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                window.chrome = { runtime: {} };
            """)

            logger.info("Justia Playwright spider browser started")
            return True

        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            return False

    async def stop_browser(self):
        """Close Playwright browser"""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
        except Exception as e:
            logger.error(f"Error stopping browser: {e}")

    async def fetch_page(self, url_path: str) -> Optional[str]:
        """Fetch a page with Cloudflare bypass"""
        page = None
        try:
            page = await self.context.new_page()

            full_url = f"{self.base_url}{url_path}"
            logger.info(f"Fetching Justia page: {full_url}")

            # Navigate with retry for Cloudflare
            for attempt in range(3):
                try:
                    await page.goto(full_url, wait_until='networkidle', timeout=60000)

                    # Check for Cloudflare challenge
                    content = await page.content()
                    if 'challenge-running' in content or 'Just a moment' in content:
                        logger.info(f"Cloudflare challenge detected, waiting... (attempt {attempt + 1})")
                        await asyncio.sleep(5)
                        continue

                    # Wait for main content
                    await asyncio.sleep(2)
                    return await page.content()

                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} failed: {e}")
                    await asyncio.sleep(3)

            return None

        except Exception as e:
            logger.error(f"Error fetching page {url_path}: {e}")
            return None

        finally:
            if page:
                await page.close()

    def parse_article_page(self, html: str, url_info: Dict) -> List[Dict[str, Any]]:
        """Parse a Justia article page for legal information"""
        articles = []

        try:
            soup = BeautifulSoup(html, 'html.parser')

            # Get main content
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')

            if not main_content:
                main_content = soup

            # Extract page title
            title_elem = soup.find('h1') or soup.find('title')
            page_title = title_elem.get_text(strip=True) if title_elem else url_info['category']

            # Extract main content text
            content_text = ""
            for elem in main_content.find_all(['p', 'li', 'h2', 'h3']):
                text = elem.get_text(strip=True)
                if text and len(text) > 20:  # Filter out short/empty elements
                    content_text += text + " "

            # Create main article entry
            if content_text:
                articles.append({
                    'title': page_title,
                    'url': f"{self.base_url}{url_info['url']}",
                    'summary': content_text[:500] + "..." if len(content_text) > 500 else content_text,
                    'full_content': content_text[:2000],
                    'category': url_info['category'],
                    'source': 'Justia',
                    'data_type': 'legal_article',
                    'tags': url_info['tags'] + ['legal_information', 'justia'],
                    'timestamp': datetime.now().isoformat(),
                    'jurisdiction': 'General (US)',
                })

            # Find links to related articles
            links = main_content.find_all('a', href=True)
            for link in links:
                href = link.get('href', '')
                link_text = link.get_text(strip=True)

                # Only include relevant family law links
                if '/family/' in href and link_text and len(link_text) > 10:
                    # Get parent paragraph for context
                    parent = link.find_parent('p')
                    context = parent.get_text(strip=True) if parent else link_text

                    full_url = href if href.startswith('http') else f"{self.base_url}{href}"

                    articles.append({
                        'title': link_text,
                        'url': full_url,
                        'summary': context[:300] if context else link_text,
                        'category': url_info['category'],
                        'source': 'Justia',
                        'data_type': 'legal_article_link',
                        'tags': url_info['tags'] + ['related', 'justia'],
                        'timestamp': datetime.now().isoformat(),
                        'jurisdiction': 'General (US)',
                    })

        except Exception as e:
            logger.error(f"Error parsing article page: {e}")

        return articles

    async def fetch_data(self, max_results: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch family law information from Justia

        Args:
            max_results: Maximum number of articles to fetch

        Returns:
            List of legal information dictionaries
        """
        all_articles = []

        try:
            if not await self.start_browser():
                logger.error("Failed to start browser, returning fallback data")
                return self._get_fallback_data()

            for url_info in self.FAMILY_LAW_URLS:
                # Fetch page
                html = await self.fetch_page(url_info['url'])

                if html:
                    # Parse articles from page
                    articles = self.parse_article_page(html, url_info)
                    all_articles.extend(articles)

                    logger.info(f"Parsed {len(articles)} items from {url_info['category']}")
                else:
                    logger.warning(f"Failed to fetch {url_info['url']}")

                # Rate limiting to avoid blocking
                await asyncio.sleep(2)

                if len(all_articles) >= max_results:
                    break

            await self.stop_browser()

        except Exception as e:
            logger.error(f"Error fetching Justia data: {e}")
            await self.stop_browser()

        # Deduplicate by URL
        seen_urls = set()
        unique_articles = []
        for article in all_articles:
            if article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                unique_articles.append(article)

        logger.info(f"Total Justia family law articles collected: {len(unique_articles)}")
        return unique_articles[:max_results]

    def _get_fallback_data(self) -> List[Dict[str, Any]]:
        """Return fallback data when browser fails"""
        fallback_articles = []

        family_law_topics = [
            {
                'title': 'Understanding Divorce Law',
                'summary': 'Comprehensive guide to divorce proceedings, including grounds for divorce, property division, and spousal support. Learn about contested vs. uncontested divorce.',
                'category': 'Divorce',
                'tags': ['divorce', 'family_law', 'dissolution'],
            },
            {
                'title': 'Child Custody Basics',
                'summary': 'Overview of child custody types including legal custody, physical custody, sole custody, and joint custody arrangements. Understand how courts determine custody.',
                'category': 'Child Custody',
                'tags': ['custody', 'children', 'family_law'],
            },
            {
                'title': 'Child Support Guidelines',
                'summary': 'How child support is calculated, factors considered by courts, modification procedures, and enforcement mechanisms for child support orders.',
                'category': 'Child Support',
                'tags': ['child_support', 'support', 'family_law'],
            },
            {
                'title': 'Parenting Time and Visitation',
                'summary': 'Understanding parenting time schedules, visitation rights for non-custodial parents, and how to modify parenting time arrangements.',
                'category': 'Parenting Time',
                'tags': ['parenting_time', 'visitation', 'custody', 'family_law'],
            },
            {
                'title': 'Best Interests of the Child Standard',
                'summary': 'Courts use the best interests of the child standard when making custody decisions. Factors include stability, parental fitness, and child preferences.',
                'category': 'Custody Standards',
                'tags': ['custody', 'best_interests', 'children', 'family_law'],
            },
            {
                'title': 'Divorce Process Overview',
                'summary': 'Step-by-step guide to the divorce process: filing petition, serving papers, discovery, negotiation, and final decree.',
                'category': 'Divorce Process',
                'tags': ['divorce', 'process', 'procedure', 'family_law'],
            },
        ]

        for topic in family_law_topics:
            fallback_articles.append({
                'title': topic['title'],
                'url': f"{self.base_url}/family/",
                'summary': topic['summary'],
                'category': topic['category'],
                'source': 'Justia',
                'data_type': 'legal_article',
                'tags': topic['tags'] + ['legal_information', 'justia', 'fallback'],
                'timestamp': datetime.now().isoformat(),
                'jurisdiction': 'General (US)',
            })

        return fallback_articles

    def fetch_data_sync(self, max_results: int = 100) -> List[Dict[str, Any]]:
        """Synchronous wrapper for fetch_data"""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(self.fetch_data(max_results))

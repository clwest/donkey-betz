"""
Playwright Spider Base - JavaScript-Enabled Web Scraping
=========================================================

Session 387: Base class for spiders that need JavaScript rendering.
Uses Playwright for headless browser automation to scrape JS-heavy sites
like Toptal, Guru, Fiverr, Kickstarter, and Indiegogo.

Features:
- Headless Chromium browser
- JavaScript execution
- Anti-bot detection measures
- Async/await support
- Automatic retry with exponential backoff
"""

import asyncio
import logging
import random
from abc import abstractmethod
from typing import Dict, List, Optional, Any
from playwright.async_api import async_playwright, Page, Browser, BrowserContext

from .base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData

logger = logging.getLogger(__name__)


class PlaywrightSpider(BaseIntelligenceSpider):
    """
    Base class for JavaScript-enabled spiders using Playwright.

    Provides:
    - Headless browser automation
    - JavaScript rendering
    - Cookie/session management
    - Anti-detection measures
    - Configurable wait strategies
    """

    # User agents for rotation
    USER_AGENTS = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    ]

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.playwright = None

        # Configuration
        self.headless = True
        self.default_timeout = 30000  # 30 seconds
        self.page_load_timeout = 60000  # 60 seconds

    async def start_browser(self):
        """Initialize Playwright browser"""
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                ]
            )

            # Create context with anti-detection settings
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent=random.choice(self.USER_AGENTS),
                locale='en-US',
                timezone_id='America/New_York',
            )

            # Anti-detection JavaScript
            await self.context.add_init_script("""
                // Override navigator.webdriver
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });

                // Override chrome property
                window.chrome = {
                    runtime: {}
                };

                // Override permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
            """)

            self.logger.info(f"Playwright browser started for spider {self.spider_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to start Playwright browser: {e}")
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
            self.logger.info(f"Playwright browser stopped for spider {self.spider_id}")
        except Exception as e:
            self.logger.error(f"Error stopping browser: {e}")

    async def fetch_with_js(self, url: str, wait_selector: Optional[str] = None,
                           wait_time: int = 2000) -> Optional[str]:
        """
        Fetch a page with JavaScript rendering.

        Args:
            url: URL to fetch
            wait_selector: CSS selector to wait for before extracting content
            wait_time: Additional time to wait after page load (ms)

        Returns:
            Page HTML content or None on failure
        """
        page = None
        try:
            if not self.context:
                await self.start_browser()

            page = await self.context.new_page()
            page.set_default_timeout(self.default_timeout)

            # Navigate to URL
            await page.goto(url, wait_until='networkidle', timeout=self.page_load_timeout)

            # Wait for specific selector if provided
            if wait_selector:
                try:
                    await page.wait_for_selector(wait_selector, timeout=10000)
                except Exception:
                    self.logger.warning(f"Selector {wait_selector} not found, continuing anyway")

            # Additional wait for dynamic content
            await asyncio.sleep(wait_time / 1000)

            # Get page content
            content = await page.content()

            self.metrics.successful_requests += 1
            return content

        except Exception as e:
            self.metrics.failed_requests += 1
            self.logger.error(f"Error fetching {url}: {e}")
            return None

        finally:
            if page:
                await page.close()

    async def fetch_json_from_page(self, url: str, api_url: str = None) -> Optional[Dict]:
        """
        Navigate to a page and extract JSON from an API call or script tag.

        Args:
            url: Page URL to visit
            api_url: Optional API URL to intercept

        Returns:
            JSON data or None
        """
        page = None
        captured_data = []

        try:
            if not self.context:
                await self.start_browser()

            page = await self.context.new_page()

            # Intercept network requests if api_url provided
            if api_url:
                async def handle_response(response):
                    if api_url in response.url:
                        try:
                            data = await response.json()
                            captured_data.append(data)
                        except:
                            pass

                page.on('response', handle_response)

            await page.goto(url, wait_until='networkidle', timeout=self.page_load_timeout)
            await asyncio.sleep(2)

            if captured_data:
                return captured_data[0]

            return None

        except Exception as e:
            self.logger.error(f"Error fetching JSON from {url}: {e}")
            return None

        finally:
            if page:
                await page.close()

    async def scroll_and_load(self, page: Page, scroll_count: int = 3,
                             scroll_delay: float = 1.0) -> None:
        """
        Scroll page to load lazy-loaded content.

        Args:
            page: Playwright page object
            scroll_count: Number of times to scroll
            scroll_delay: Delay between scrolls in seconds
        """
        for _ in range(scroll_count):
            await page.evaluate('window.scrollBy(0, window.innerHeight)')
            await asyncio.sleep(scroll_delay)

    async def run_once(self) -> List[Dict[str, Any]]:
        """
        Run a single scraping session.

        Returns:
            List of collected data items
        """
        try:
            await self.start_browser()

            all_data = []
            for target in self.targets:
                try:
                    data = await self.fetch_data(target)
                    if data:
                        intelligence = await self.process_data(data, target)
                        if intelligence:
                            all_data.append({
                                'intelligence': intelligence,
                                'raw_data': data
                            })
                            await self._distribute_intelligence(intelligence)
                except Exception as e:
                    self.logger.error(f"Error processing target {target.url}: {e}")

                # Random delay between requests
                await asyncio.sleep(random.uniform(1, 3))

            return all_data

        finally:
            await self.stop_browser()

    @abstractmethod
    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """
        Fetch data from target using Playwright.
        Must be implemented by subclasses.
        """

    @abstractmethod
    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """
        Process raw data into intelligence.
        Must be implemented by subclasses.
        """

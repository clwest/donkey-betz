"""
Fiverr Spider - JavaScript-Enabled Freelance Gig Scraper
=========================================================

Session 387: Playwright-based spider for scraping Fiverr gigs.
Uses JavaScript rendering to extract real freelance opportunities.

Target Categories:
- Programming & Tech
- Graphics & Design
- Digital Marketing
- Writing & Translation
- AI Services
"""

import re
import json
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup

from ..playwright_spider import PlaywrightSpider
from ..base_spider import SpiderTarget, IntelligenceData


class FiverrPlaywrightSpider(PlaywrightSpider):
    """
    Fiverr spider using Playwright for JavaScript rendering.

    Scrapes:
    - Gig listings from category pages
    - Seller information
    - Pricing and packages
    - Ratings and reviews
    """

    # Target categories and their URLs
    CATEGORIES = {
        'programming': 'https://www.fiverr.com/categories/programming-tech',
        'graphics': 'https://www.fiverr.com/categories/graphics-design',
        'digital_marketing': 'https://www.fiverr.com/categories/online-marketing',
        'writing': 'https://www.fiverr.com/categories/writing-translation',
        'ai_services': 'https://www.fiverr.com/categories/ai-services',
    }

    def __init__(self, spider_id: str = 'fiverr_playwright',
                 targets: List[SpiderTarget] = None,
                 subscribers: List[str] = None,
                 redis_config: Dict[str, Any] = None):

        # Create targets from categories if not provided
        if targets is None:
            targets = [
                SpiderTarget(
                    url=url,
                    headers={},
                    rate_limit=0.5,  # 1 request per 2 seconds
                    priority=1,
                    timeout=60
                )
                for url in self.CATEGORIES.values()
            ]

        super().__init__(spider_id, targets, subscribers or [], redis_config or {})

        self.collected_gigs = []

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """
        Fetch gig listings from Fiverr category page.
        """
        try:
            # Fetch page with JS rendering
            html = await self.fetch_with_js(
                target.url,
                wait_selector='.gig-card-layout',  # Wait for gig cards
                wait_time=3000
            )

            if not html:
                self.logger.warning(f"No HTML returned from {target.url}")
                return None

            return {
                'html': html,
                'url': target.url,
                'category': self._get_category_from_url(target.url)
            }

        except Exception as e:
            self.logger.error(f"Error fetching Fiverr data: {e}")
            return None

    def _get_category_from_url(self, url: str) -> str:
        """Extract category name from URL"""
        for cat_name, cat_url in self.CATEGORIES.items():
            if cat_url in url:
                return cat_name
        return 'unknown'

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """
        Parse Fiverr HTML and extract gig information.
        """
        try:
            html = raw_data.get('html', '')
            category = raw_data.get('category', 'unknown')

            soup = BeautifulSoup(html, 'html.parser')
            gigs = []

            # Find gig cards - Fiverr uses various card classes
            gig_cards = soup.select('.gig-card-layout, .gig-wrapper, [class*="GigCard"]')

            if not gig_cards:
                # Try alternative selectors
                gig_cards = soup.select('article, .listing-item, [data-testid*="gig"]')

            self.logger.info(f"Found {len(gig_cards)} gig cards on {target.url}")

            for card in gig_cards[:20]:  # Limit to 20 per page
                try:
                    gig = self._parse_gig_card(card, category)
                    if gig:
                        gigs.append(gig)
                except Exception as e:
                    self.logger.debug(f"Error parsing gig card: {e}")
                    continue

            if not gigs:
                self.logger.warning(f"No gigs extracted from {target.url}")
                return None

            # Store collected gigs
            self.collected_gigs.extend(gigs)

            # Calculate quality score
            quality_score = min(1.0, len(gigs) / 10)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url=target.url,
                data_type='job_posting',
                content={
                    'gigs': gigs,
                    'category': category,
                    'total_found': len(gigs),
                    'source': 'fiverr'
                },
                metadata={
                    'spider_type': 'playwright',
                    'category': category,
                    'extraction_method': 'html_parsing',
                    'js_rendered': True
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['fiverr', 'freelance', 'gigs', category],
                target_agents=['opportunity_scoring_agent', 'research_agent'],
                target_advisors=[]
            )

        except Exception as e:
            self.logger.error(f"Error processing Fiverr data: {e}")
            return None

    def _parse_gig_card(self, card, category: str) -> Optional[Dict[str, Any]]:
        """
        Parse a single Fiverr gig card.
        """
        try:
            # Extract title
            title_elem = card.select_one('h3, .gig-title, [class*="title"], a[href*="/"]')
            title = title_elem.get_text(strip=True) if title_elem else None

            if not title or len(title) < 5:
                return None

            # Extract seller info
            seller_elem = card.select_one('.seller-name, [class*="seller"], .username')
            seller = seller_elem.get_text(strip=True) if seller_elem else 'Unknown'

            # Extract price
            price_elem = card.select_one('.price, [class*="price"], .gig-price')
            price_text = price_elem.get_text(strip=True) if price_elem else '$0'
            price = self._parse_price(price_text)

            # Extract rating
            rating_elem = card.select_one('.rating-score, [class*="rating"], .stars')
            rating_text = rating_elem.get_text(strip=True) if rating_elem else '0'
            rating = self._parse_rating(rating_text)

            # Extract reviews count
            reviews_elem = card.select_one('.ratings-count, [class*="reviews"], .reviews')
            reviews_text = reviews_elem.get_text(strip=True) if reviews_elem else '0'
            reviews = self._parse_number(reviews_text)

            # Extract URL
            link_elem = card.select_one('a[href*="/"]')
            gig_url = ''
            if link_elem and link_elem.get('href'):
                href = link_elem.get('href')
                if href.startswith('/'):
                    gig_url = f'https://www.fiverr.com{href}'
                elif href.startswith('http'):
                    gig_url = href

            # Extract image
            img_elem = card.select_one('img')
            image_url = img_elem.get('src', '') if img_elem else ''

            return {
                'id': f"fiverr_{hash(title + seller) % 1000000}",
                'title': title,
                'seller': seller,
                'price': price,
                'price_text': price_text,
                'rating': rating,
                'reviews': reviews,
                'url': gig_url,
                'image_url': image_url,
                'category': category,
                'platform': 'fiverr',
                'source': 'fiverr',
                'fetched_at': datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            self.logger.debug(f"Error parsing gig card: {e}")
            return None

    def _parse_price(self, text: str) -> float:
        """Extract numeric price from text"""
        try:
            # Remove currency symbols and parse
            numbers = re.findall(r'[\d,]+\.?\d*', text.replace(',', ''))
            if numbers:
                return float(numbers[0])
            return 0.0
        except:
            return 0.0

    def _parse_rating(self, text: str) -> float:
        """Extract rating from text"""
        try:
            numbers = re.findall(r'[\d.]+', text)
            if numbers:
                return min(5.0, float(numbers[0]))
            return 0.0
        except:
            return 0.0

    def _parse_number(self, text: str) -> int:
        """Extract number from text (e.g., '1.2k' -> 1200)"""
        try:
            text = text.lower().replace(',', '')
            if 'k' in text:
                return int(float(text.replace('k', '')) * 1000)
            numbers = re.findall(r'\d+', text)
            if numbers:
                return int(numbers[0])
            return 0
        except:
            return 0

    async def get_collected_data(self) -> List[Dict[str, Any]]:
        """Return all collected gigs"""
        return self.collected_gigs

    def get_required_fields(self) -> List[str]:
        return ['title', 'seller', 'price']

    def get_relevance_keywords(self) -> List[str]:
        return ['fiverr', 'freelance', 'gig', 'service', 'design', 'development', 'writing']


# Standalone function to run the spider
async def run_fiverr_spider() -> List[Dict[str, Any]]:
    """
    Run the Fiverr spider and return collected gigs.
    """
    spider = FiverrPlaywrightSpider()
    results = await spider.run_once()
    return spider.collected_gigs

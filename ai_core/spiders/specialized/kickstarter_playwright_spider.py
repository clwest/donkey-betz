"""
Kickstarter Spider - JavaScript-Enabled Crowdfunding Scraper
=============================================================

Session 387: Playwright-based spider for scraping Kickstarter projects.
Uses JavaScript rendering to extract real crowdfunding campaigns.

Target Categories:
- Technology
- Design
- Games
- Film & Video
- Art
"""

import re
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup

from ..playwright_spider import PlaywrightSpider
from ..base_spider import SpiderTarget, IntelligenceData


import logging
logger = logging.getLogger(__name__)

class KickstarterPlaywrightSpider(PlaywrightSpider):
    """
    Kickstarter spider using Playwright for JavaScript rendering.

    Scrapes:
    - Project listings from category/discover pages
    - Funding progress
    - Creator information
    - Project descriptions
    """

    # Target categories and their URLs
    CATEGORIES = {
        'technology': 'https://www.kickstarter.com/discover/advanced?category_id=16&sort=magic',
        'design': 'https://www.kickstarter.com/discover/advanced?category_id=7&sort=magic',
        'games': 'https://www.kickstarter.com/discover/advanced?category_id=12&sort=magic',
        'film': 'https://www.kickstarter.com/discover/advanced?category_id=11&sort=magic',
        'art': 'https://www.kickstarter.com/discover/advanced?category_id=1&sort=magic',
    }

    def __init__(self, spider_id: str = 'kickstarter_playwright',
                 targets: List[SpiderTarget] = None,
                 subscribers: List[str] = None,
                 redis_config: Dict[str, Any] = None):

        # Create targets from categories if not provided
        if targets is None:
            targets = [
                SpiderTarget(
                    url=url,
                    headers={},
                    rate_limit=0.3,  # 1 request per 3 seconds
                    priority=1,
                    timeout=60
                )
                for url in self.CATEGORIES.values()
            ]

        super().__init__(spider_id, targets, subscribers or [], redis_config or {})

        self.collected_projects = []

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """
        Fetch project listings from Kickstarter discover page.
        """
        try:
            # Fetch page with JS rendering
            html = await self.fetch_with_js(
                target.url,
                wait_selector='.js-react-proj-card, .project-card',
                wait_time=4000  # Kickstarter loads slowly
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
            self.logger.error(f"Error fetching Kickstarter data: {e}")
            return None

    def _get_category_from_url(self, url: str) -> str:
        """Extract category name from URL"""
        for cat_name, cat_url in self.CATEGORIES.items():
            if cat_url == url:
                return cat_name
        return 'unknown'

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """
        Parse Kickstarter HTML and extract project information.
        """
        try:
            html = raw_data.get('html', '')
            category = raw_data.get('category', 'unknown')

            soup = BeautifulSoup(html, 'html.parser')
            projects = []

            # Find project cards
            project_cards = soup.select('.js-react-proj-card, .project-card, [data-pid], article')

            if not project_cards:
                # Try alternative selectors
                project_cards = soup.select('[class*="ProjectCard"], [class*="project"]')

            self.logger.info(f"Found {len(project_cards)} project cards on {target.url}")

            for card in project_cards[:20]:  # Limit to 20 per page
                try:
                    project = self._parse_project_card(card, category)
                    if project:
                        projects.append(project)
                except Exception as e:
                    self.logger.debug(f"Error parsing project card: {e}")
                    continue

            if not projects:
                self.logger.warning(f"No projects extracted from {target.url}")
                return None

            # Store collected projects
            self.collected_projects.extend(projects)

            # Calculate quality score
            quality_score = min(1.0, len(projects) / 10)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url=target.url,
                data_type='product_info',
                content={
                    'projects': projects,
                    'category': category,
                    'total_found': len(projects),
                    'source': 'kickstarter'
                },
                metadata={
                    'spider_type': 'playwright',
                    'category': category,
                    'extraction_method': 'html_parsing',
                    'js_rendered': True
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['kickstarter', 'crowdfunding', 'projects', category],
                target_agents=['opportunity_scoring_agent', 'trend_analysis_agent'],
                target_advisors=[]
            )

        except Exception as e:
            self.logger.error(f"Error processing Kickstarter data: {e}")
            return None

    def _parse_project_card(self, card, category: str) -> Optional[Dict[str, Any]]:
        """
        Parse a single Kickstarter project card.
        """
        try:
            # Extract title
            title_elem = card.select_one('h3, h2, .project-title, [class*="title"]')
            title = title_elem.get_text(strip=True) if title_elem else None

            if not title or len(title) < 5:
                return None

            # Extract creator
            creator_elem = card.select_one('.creator-name, [class*="creator"], .by')
            creator = creator_elem.get_text(strip=True).replace('by ', '') if creator_elem else 'Unknown'

            # Extract funding info
            pledged_elem = card.select_one('.money, [class*="pledged"], [class*="amount"]')
            pledged_text = pledged_elem.get_text(strip=True) if pledged_elem else '$0'
            pledged = self._parse_money(pledged_text)

            goal_elem = card.select_one('[class*="goal"], .funding-goal')
            goal_text = goal_elem.get_text(strip=True) if goal_elem else '$0'
            goal = self._parse_money(goal_text)

            # Calculate funding percentage
            funded_percent = (pledged / goal * 100) if goal > 0 else 0

            # Extract backers count
            backers_elem = card.select_one('[class*="backer"], .num-backers')
            backers_text = backers_elem.get_text(strip=True) if backers_elem else '0'
            backers = self._parse_number(backers_text)

            # Extract days left
            days_elem = card.select_one('[class*="days"], .time-left')
            days_text = days_elem.get_text(strip=True) if days_elem else ''
            days_left = self._parse_number(days_text)

            # Extract URL
            link_elem = card.select_one('a[href*="/projects/"]')
            project_url = ''
            if link_elem and link_elem.get('href'):
                href = link_elem.get('href')
                if href.startswith('/'):
                    project_url = f'https://www.kickstarter.com{href}'
                elif href.startswith('http'):
                    project_url = href

            # Extract image
            img_elem = card.select_one('img')
            image_url = img_elem.get('src', '') if img_elem else ''

            # Extract description/blurb
            desc_elem = card.select_one('.project-blurb, [class*="blurb"], p')
            description = desc_elem.get_text(strip=True)[:300] if desc_elem else ''

            return {
                'id': f"ks_{hash(title + creator) % 1000000}",
                'title': title,
                'creator': creator,
                'description': description,
                'pledged': pledged,
                'pledged_text': pledged_text,
                'goal': goal,
                'goal_text': goal_text,
                'funded_percent': round(funded_percent, 1),
                'backers': backers,
                'days_left': days_left,
                'url': project_url,
                'image_url': image_url,
                'category': category,
                'platform': 'kickstarter',
                'source': 'kickstarter',
                'fetched_at': datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            self.logger.debug(f"Error parsing project card: {e}")
            return None

    def _parse_money(self, text: str) -> float:
        """Extract numeric amount from money text"""
        try:
            # Remove currency symbols and parse
            text = text.replace(',', '').replace('$', '').replace('€', '').replace('£', '')
            numbers = re.findall(r'[\d.]+', text)
            if numbers:
                return float(numbers[0])
            return 0.0
        except Exception as _e:
            logger.warning(
                "kickstarter_playwright_spider._parse_money: swallowed (%s: %s) — returning default",
                type(_e).__name__, _e,
            )
            return 0.0

    def _parse_number(self, text: str) -> int:
        """Extract number from text"""
        try:
            text = text.lower().replace(',', '')
            numbers = re.findall(r'\d+', text)
            if numbers:
                return int(numbers[0])
            return 0
        except Exception as _e:
            logger.warning(
                "kickstarter_playwright_spider._parse_number: swallowed (%s: %s) — returning default",
                type(_e).__name__, _e,
            )
            return 0

    async def get_collected_data(self) -> List[Dict[str, Any]]:
        """Return all collected projects"""
        return self.collected_projects

    def get_required_fields(self) -> List[str]:
        return ['title', 'creator']

    def get_relevance_keywords(self) -> List[str]:
        return ['kickstarter', 'crowdfunding', 'project', 'campaign', 'backing', 'pledge']


# Standalone function to run the spider
async def run_kickstarter_spider() -> List[Dict[str, Any]]:
    """
    Run the Kickstarter spider and return collected projects.
    """
    spider = KickstarterPlaywrightSpider()
    results = await spider.run_once()
    return spider.collected_projects

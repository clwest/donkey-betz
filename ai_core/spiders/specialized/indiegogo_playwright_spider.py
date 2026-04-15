"""
Indiegogo Spider - JavaScript-Enabled Crowdfunding Scraper
===========================================================

Session 387: Playwright-based spider for scraping Indiegogo campaigns.
Uses JavaScript rendering to extract real crowdfunding projects.

Target Categories:
- Technology & Innovation
- Design & Production
- Film & Video
- Health & Fitness
- Community Projects
"""

import re
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup

from ..playwright_spider import PlaywrightSpider
from ..base_spider import SpiderTarget, IntelligenceData


import logging
logger = logging.getLogger(__name__)

class IndiegogoPlaywrightSpider(PlaywrightSpider):
    """
    Indiegogo spider using Playwright for JavaScript rendering.

    Scrapes:
    - Campaign listings from explore pages
    - Funding progress and goals
    - Creator information
    - Campaign descriptions
    """

    # Target categories and their URLs
    CATEGORIES = {
        'technology': 'https://www.indiegogo.com/explore/technology-innovation',
        'design': 'https://www.indiegogo.com/explore/design-art',
        'film': 'https://www.indiegogo.com/explore/film',
        'health': 'https://www.indiegogo.com/explore/health-fitness',
        'community': 'https://www.indiegogo.com/explore/community',
    }

    def __init__(self, spider_id: str = 'indiegogo_playwright',
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

        self.collected_campaigns = []

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """
        Fetch campaign listings from Indiegogo explore page.
        """
        try:
            # Fetch page with JS rendering
            html = await self.fetch_with_js(
                target.url,
                wait_selector='.discoverableCard, .campaignCard, [class*="CampaignCard"]',
                wait_time=4000
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
            self.logger.error(f"Error fetching Indiegogo data: {e}")
            return None

    def _get_category_from_url(self, url: str) -> str:
        """Extract category name from URL"""
        for cat_name, cat_url in self.CATEGORIES.items():
            if cat_url == url:
                return cat_name
        return 'unknown'

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """
        Parse Indiegogo HTML and extract campaign information.
        """
        try:
            html = raw_data.get('html', '')
            category = raw_data.get('category', 'unknown')

            soup = BeautifulSoup(html, 'html.parser')
            campaigns = []

            # Find campaign cards
            campaign_cards = soup.select('.discoverableCard, .campaignCard, [class*="CampaignCard"], article')

            if not campaign_cards:
                # Try alternative selectors
                campaign_cards = soup.select('[data-testid*="campaign"], .explore-card, .project-card')

            self.logger.info(f"Found {len(campaign_cards)} campaign cards on {target.url}")

            for card in campaign_cards[:20]:  # Limit to 20 per page
                try:
                    campaign = self._parse_campaign_card(card, category)
                    if campaign:
                        campaigns.append(campaign)
                except Exception as e:
                    self.logger.debug(f"Error parsing campaign card: {e}")
                    continue

            if not campaigns:
                self.logger.warning(f"No campaigns extracted from {target.url}")
                return None

            # Store collected campaigns
            self.collected_campaigns.extend(campaigns)

            # Calculate quality score
            quality_score = min(1.0, len(campaigns) / 10)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url=target.url,
                data_type='product_info',
                content={
                    'campaigns': campaigns,
                    'category': category,
                    'total_found': len(campaigns),
                    'source': 'indiegogo'
                },
                metadata={
                    'spider_type': 'playwright',
                    'category': category,
                    'extraction_method': 'html_parsing',
                    'js_rendered': True
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['indiegogo', 'crowdfunding', 'campaigns', category],
                target_agents=['opportunity_scoring_agent', 'trend_analysis_agent'],
                target_advisors=[]
            )

        except Exception as e:
            self.logger.error(f"Error processing Indiegogo data: {e}")
            return None

    def _parse_campaign_card(self, card, category: str) -> Optional[Dict[str, Any]]:
        """
        Parse a single Indiegogo campaign card.
        """
        try:
            # Extract title
            title_elem = card.select_one('h3, h2, .cardTitle, [class*="title"], .campaign-title')
            title = title_elem.get_text(strip=True) if title_elem else None

            if not title or len(title) < 5:
                return None

            # Extract creator/team name
            creator_elem = card.select_one('.cardTeamName, [class*="creator"], [class*="team"], .by-line')
            creator = creator_elem.get_text(strip=True) if creator_elem else 'Unknown'

            # Extract funding info
            raised_elem = card.select_one('.cardAmountRaised, [class*="raised"], [class*="amount"]')
            raised_text = raised_elem.get_text(strip=True) if raised_elem else '$0'
            raised = self._parse_money(raised_text)

            goal_elem = card.select_one('[class*="goal"], .funding-goal')
            goal_text = goal_elem.get_text(strip=True) if goal_elem else '$0'
            goal = self._parse_money(goal_text)

            # Extract percentage funded
            percent_elem = card.select_one('.cardPercentFunded, [class*="percent"], .progress-text')
            percent_text = percent_elem.get_text(strip=True) if percent_elem else '0'
            funded_percent = self._parse_percent(percent_text)

            if funded_percent == 0 and goal > 0:
                funded_percent = (raised / goal * 100)

            # Extract backers count
            backers_elem = card.select_one('[class*="backer"], .backers-count')
            backers_text = backers_elem.get_text(strip=True) if backers_elem else '0'
            backers = self._parse_number(backers_text)

            # Extract days left
            days_elem = card.select_one('[class*="days"], .time-remaining')
            days_text = days_elem.get_text(strip=True) if days_elem else ''
            days_left = self._parse_number(days_text)

            # Extract URL
            link_elem = card.select_one('a[href*="/projects/"]')
            campaign_url = ''
            if link_elem and link_elem.get('href'):
                href = link_elem.get('href')
                if href.startswith('/'):
                    campaign_url = f'https://www.indiegogo.com{href}'
                elif href.startswith('http'):
                    campaign_url = href

            # Extract image
            img_elem = card.select_one('img')
            image_url = img_elem.get('src', '') if img_elem else ''

            # Extract description/tagline
            desc_elem = card.select_one('.cardTagline, [class*="tagline"], [class*="description"], p')
            description = desc_elem.get_text(strip=True)[:300] if desc_elem else ''

            # Check if InDemand (post-campaign)
            indemand_elem = card.select_one('[class*="indemand"], .inDemand')
            is_indemand = indemand_elem is not None

            return {
                'id': f"igg_{hash(title + creator) % 1000000}",
                'title': title,
                'creator': creator,
                'description': description,
                'raised': raised,
                'raised_text': raised_text,
                'goal': goal,
                'goal_text': goal_text,
                'funded_percent': round(funded_percent, 1),
                'backers': backers,
                'days_left': days_left,
                'url': campaign_url,
                'image_url': image_url,
                'category': category,
                'is_indemand': is_indemand,
                'platform': 'indiegogo',
                'source': 'indiegogo',
                'fetched_at': datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            self.logger.debug(f"Error parsing campaign card: {e}")
            return None

    def _parse_money(self, text: str) -> float:
        """Extract numeric amount from money text"""
        try:
            text = text.replace(',', '').replace('$', '').replace('€', '').replace('£', '')
            numbers = re.findall(r'[\d.]+', text)
            if numbers:
                return float(numbers[0])
            return 0.0
        except Exception as _e:
            logger.warning(
                "indiegogo_playwright_spider._parse_money: swallowed (%s: %s) — returning default",
                type(_e).__name__, _e,
            )
            return 0.0

    def _parse_percent(self, text: str) -> float:
        """Extract percentage from text"""
        try:
            numbers = re.findall(r'[\d.]+', text.replace(',', ''))
            if numbers:
                return float(numbers[0])
            return 0.0
        except Exception as _e:
            logger.warning(
                "indiegogo_playwright_spider._parse_percent: swallowed (%s: %s) — returning default",
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
                "indiegogo_playwright_spider._parse_number: swallowed (%s: %s) — returning default",
                type(_e).__name__, _e,
            )
            return 0

    async def get_collected_data(self) -> List[Dict[str, Any]]:
        """Return all collected campaigns"""
        return self.collected_campaigns

    def get_required_fields(self) -> List[str]:
        return ['title', 'creator']

    def get_relevance_keywords(self) -> List[str]:
        return ['indiegogo', 'crowdfunding', 'campaign', 'backing', 'innovation', 'startup']


# Standalone function to run the spider
async def run_indiegogo_spider() -> List[Dict[str, Any]]:
    """
    Run the Indiegogo spider and return collected campaigns.
    """
    spider = IndiegogoPlaywrightSpider()
    results = await spider.run_once()
    return spider.collected_campaigns

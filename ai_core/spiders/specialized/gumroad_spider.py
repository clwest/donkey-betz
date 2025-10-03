"""
Gumroad Intelligence Spider - Digital Products Platform
======================================================

Specialized spider for gathering digital product opportunities from Gumroad.
"""

import re
import json
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData
from ..revenue_tracker import create_project_revenue


class GumroadIntelligenceSpider(BaseIntelligenceSpider):
    """Gumroad digital products intelligence spider."""

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)
        self.product_categories = ['templates', 'courses', 'ebooks', 'software', 'graphics']

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process Gumroad data"""
        try:
            if 'gumroad.com' in target.url:
                return await self._process_gumroad_product(raw_data, target)
            return None
        except Exception as e:
            self.logger.error(f"Error processing Gumroad data: {e}")
            return None

    async def _process_gumroad_product(self, data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process Gumroad product"""
        if 'content' not in data:
            return None

        soup = BeautifulSoup(data['content'], 'html.parser')

        product_info = {
            'id': f"gumroad_{int(datetime.now().timestamp())}",
            'title': self._extract_title(soup),
            'creator': self._extract_creator(soup),
            'price': self._extract_price(soup),
            'sales_count': self._extract_sales(soup),
            'rating': self._extract_rating(soup),
            'category': self._extract_category(soup),
            'tags': self._extract_tags(soup),
            'source': 'gumroad'
        }

        return IntelligenceData(
            spider_id=self.spider_id,
            source_url=target.url,
            data_type='digital_product_opportunity',
            content=product_info,
            metadata={'platform': 'gumroad', 'product_type': 'digital'},
            quality_score=0.7,
            timestamp=datetime.now(timezone.utc),
            relevance_tags=['digital_products', 'gumroad', 'monetization'],
            target_agents=['income_builder', 'digital_product_creator'],
            target_advisors=['creator_economy_expert']
        )

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract product title"""
        for selector in ['h1', '.product-title', '[data-testid="title"]']:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text().strip()
        return "Gumroad Product"

    def _extract_creator(self, soup: BeautifulSoup) -> str:
        """Extract creator name"""
        for selector in ['.creator-name', '.author', '[data-testid="creator"]']:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text().strip()
        return "Unknown Creator"

    def _extract_price(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract product price"""
        text = soup.get_text()
        price_match = re.search(r'\$[\d,]+(?:\.\d{2})?', text)
        return price_match.group() if price_match else None

    def _extract_sales(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract sales count"""
        text = soup.get_text()
        sales_match = re.search(r'(\d+(?:,\d{3})*)\s*sales?', text, re.IGNORECASE)
        return int(sales_match.group(1).replace(',', '')) if sales_match else None

    def _extract_rating(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract product rating"""
        text = soup.get_text()
        rating_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:stars?|rating)', text, re.IGNORECASE)
        return float(rating_match.group(1)) if rating_match else None

    def _extract_category(self, soup: BeautifulSoup) -> str:
        """Extract product category"""
        for category in self.product_categories:
            if category in soup.get_text().lower():
                return category
        return 'digital'

    def _extract_tags(self, soup: BeautifulSoup) -> List[str]:
        """Extract product tags"""
        tags = []
        for elem in soup.select('.tag, .category, .label'):
            tag = elem.get_text().strip()
            if tag and len(tag) < 30:
                tags.append(tag)
        return tags[:10]

    async def track_revenue_conversion(
        self,
        application_id: str,
        user_id: str,
        product_title: str,
        sale_amount: float,
        client_name: str = "Gumroad Marketplace",
        **kwargs
    ) -> Optional[str]:
        """
        Track revenue when a Gumroad product makes a sale.
        Called when product sales occur.

        Args:
            application_id: Unique identifier for this product opportunity
            user_id: User who created/sold the product
            product_title: Title of the product that generated revenue
            sale_amount: Amount earned from the sale
            client_name: Platform or buyer name (defaults to Gumroad)
            **kwargs: Additional metadata (product_category, buyer_info, etc.)

        Returns:
            Revenue record ID if successful, None otherwise
        """
        try:
            record_id = await create_project_revenue(
                application_id=application_id,
                user_id=user_id,
                client_name=client_name,
                project_title=product_title,
                contract_value=sale_amount,
                **kwargs
            )

            if record_id:
                self.logger.info(f"💰 Tracked Gumroad revenue: ${sale_amount} for '{product_title}'")

            return record_id

        except Exception as e:
            self.logger.error(f"Error tracking Gumroad revenue conversion: {e}")
            return None
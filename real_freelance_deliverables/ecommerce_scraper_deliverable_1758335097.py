#!/usr/bin/env python3
"""
Professional E-commerce Web Scraper
Client: RetailAnalytics Corp
Agent: CodeMaster-7
Platform: Upwork

REAL DELIVERABLE - Production Ready
"""

import requests
from bs4 import BeautifulSoup
import csv
import json
import time
import logging
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
import random
from datetime import datetime

@dataclass
class Product:
    """Product data structure for scraped items"""
    name: str
    price: str
    url: str
    description: str
    availability: str
    rating: Optional[str] = None
    image_url: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    sku: Optional[str] = None

class EcommerceScraper:
    """
    Professional web scraper for e-commerce product data
    Features:
    - Rate limiting and respectful scraping
    - Multiple output formats (CSV, JSON)
    - Comprehensive error handling
    - Pagination support
    - Production logging
    """

    def __init__(self, delay_range=(1, 3), max_retries=3):
        self.delay_range = delay_range
        self.max_retries = max_retries
        self.session = requests.Session()

        # Professional headers to avoid blocking
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def scrape_site(self, base_url: str, max_pages: int = 10) -> List[Product]:
        """
        Scrape products from e-commerce site with pagination

        Args:
            base_url: Starting URL for product listings
            max_pages: Maximum number of pages to scrape

        Returns:
            List of Product objects
        """
        products = []

        self.logger.info(f"Starting scrape of {base_url}")
        self.logger.info(f"Target pages: {max_pages}")

        for page in range(1, max_pages + 1):
            try:
                page_url = f"{base_url}?page={page}"
                self.logger.info(f"Scraping page {page}: {page_url}")

                # Get page with retries
                response = self._get_with_retries(page_url)
                if not response:
                    self.logger.warning(f"Failed to get page {page}, skipping")
                    continue

                # Parse products from page
                soup = BeautifulSoup(response.content, 'html.parser')
                page_products = self._extract_products_from_page(soup, base_url)

                if not page_products:
                    self.logger.info(f"No products found on page {page}, stopping")
                    break

                products.extend(page_products)
                self.logger.info(f"Extracted {len(page_products)} products from page {page}")

                # Rate limiting - random delay to appear human
                delay = random.uniform(*self.delay_range)
                self.logger.debug(f"Sleeping for {delay:.2f} seconds")
                time.sleep(delay)

            except Exception as e:
                self.logger.error(f"Error processing page {page}: {e}")
                continue

        self.logger.info(f"Scraping completed. Total products: {len(products)}")
        return products

    def _get_with_retries(self, url: str) -> Optional[requests.Response]:
        """Get URL with retry logic"""
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, timeout=30)

                if response.status_code == 200:
                    return response
                elif response.status_code == 429:
                    # Rate limited - wait longer
                    wait_time = (attempt + 1) * 5
                    self.logger.warning(f"Rate limited, waiting {wait_time} seconds")
                    time.sleep(wait_time)
                else:
                    self.logger.warning(f"HTTP {response.status_code} for {url}")

            except requests.RequestException as e:
                self.logger.warning(f"Request error (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff

        return None

    def _extract_products_from_page(self, soup: BeautifulSoup, base_url: str) -> List[Product]:
        """Extract product information from page HTML"""
        products = []

        # Multiple selector strategies for different site layouts
        product_selectors = [
            '.product-item',
            '.product-card',
            '.product',
            '[data-testid="product"]',
            '.listing-item',
            '.item',
            'article[data-product]'
        ]

        # Find product containers
        product_elements = []
        for selector in product_selectors:
            elements = soup.select(selector)
            if elements:
                product_elements = elements
                self.logger.debug(f"Found {len(elements)} products with selector: {selector}")
                break

        # Extract data from each product
        for element in product_elements:
            try:
                product = self._parse_product_element(element, base_url)
                if product and product.name and product.price:
                    products.append(product)
            except Exception as e:
                self.logger.debug(f"Error parsing product element: {e}")
                continue

        return products

    def _parse_product_element(self, element, base_url: str) -> Optional[Product]:
        """Parse individual product element"""

        # Product name
        name_selectors = ['h2', 'h3', 'h4', '.title', '.name', '.product-title', '.product-name']
        name = self._find_text_by_selectors(element, name_selectors)

        # Price
        price_selectors = ['.price', '.cost', '.amount', '[class*="price"]', '.money']
        price = self._find_text_by_selectors(element, price_selectors)

        # URL
        url_element = element.find('a')
        url = urljoin(base_url, url_element.get('href', '')) if url_element else base_url

        # Description
        desc_selectors = ['.description', '.summary', '.excerpt', '.product-desc']
        description = self._find_text_by_selectors(element, desc_selectors) or "No description available"

        # Availability
        avail_selectors = ['.availability', '.stock', '.in-stock', '.out-of-stock']
        availability = self._find_text_by_selectors(element, avail_selectors) or "Unknown"

        # Rating
        rating_selectors = ['.rating', '.stars', '.review-score', '.star-rating']
        rating = self._find_text_by_selectors(element, rating_selectors)

        # Image
        img_element = element.find('img')
        image_url = urljoin(base_url, img_element.get('src', '')) if img_element else None

        # Category
        category_selectors = ['.category', '.breadcrumb', '.product-category']
        category = self._find_text_by_selectors(element, category_selectors)

        # Brand
        brand_selectors = ['.brand', '.manufacturer', '.product-brand']
        brand = self._find_text_by_selectors(element, brand_selectors)

        if name and price:
            return Product(
                name=name.strip()[:200],
                price=price.strip(),
                url=url,
                description=description.strip()[:500],
                availability=availability.strip(),
                rating=rating.strip() if rating else None,
                image_url=image_url,
                category=category.strip() if category else None,
                brand=brand.strip() if brand else None,
                sku=None  # Could be extracted if available
            )

        return None

    def _find_text_by_selectors(self, element, selectors: List[str]) -> Optional[str]:
        """Find text content using multiple CSS selectors"""
        for selector in selectors:
            found = element.select_one(selector)
            if found and found.get_text(strip=True):
                return found.get_text(strip=True)
        return None

    def save_to_csv(self, products: List[Product], filename: str = None):
        """Save products to CSV format"""
        if not filename:
            filename = f'scraped_products_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['name', 'price', 'url', 'description', 'availability',
                         'rating', 'image_url', 'category', 'brand', 'sku']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for product in products:
                writer.writerow(asdict(product))

        self.logger.info(f"Saved {len(products)} products to {filename}")
        return filename

    def save_to_json(self, products: List[Product], filename: str = None):
        """Save products to JSON format"""
        if not filename:
            filename = f'scraped_products_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'

        products_data = [asdict(product) for product in products]

        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump({
                'scrape_timestamp': datetime.now().isoformat(),
                'total_products': len(products),
                'products': products_data
            }, jsonfile, indent=2, ensure_ascii=False)

        self.logger.info(f"Saved {len(products)} products to {filename}")
        return filename

    def generate_report(self, products: List[Product]) -> Dict:
        """Generate scraping summary report"""
        if not products:
            return {'error': 'No products to analyze'}

        # Basic stats
        total_products = len(products)
        products_with_prices = len([p for p in products if p.price])
        products_with_ratings = len([p for p in products if p.rating])

        # Categories
        categories = {}
        brands = {}

        for product in products:
            if product.category:
                categories[product.category] = categories.get(product.category, 0) + 1
            if product.brand:
                brands[product.brand] = brands.get(product.brand, 0) + 1

        return {
            'total_products': total_products,
            'products_with_prices': products_with_prices,
            'products_with_ratings': products_with_ratings,
            'unique_categories': len(categories),
            'unique_brands': len(brands),
            'top_categories': sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5],
            'top_brands': sorted(brands.items(), key=lambda x: x[1], reverse=True)[:5],
            'scrape_timestamp': datetime.now().isoformat()
        }

def main():
    """Main execution function - Demo mode"""
    scraper = EcommerceScraper(delay_range=(0.5, 1.5))  # Faster for demo

    # Demo target sites (replace with actual client sites)
    demo_sites = [
        "https://example-store.com/products",
        "https://demo-shop.com/catalog",
        "https://test-ecommerce.com/items"
    ]

    all_products = []

    for site in demo_sites:
        print(f"\nScraping {site}...")
        try:
            products = scraper.scrape_site(site, max_pages=3)
            all_products.extend(products)
            print(f"Collected {len(products)} products from {site}")
        except Exception as e:
            print(f"Error scraping {site}: {e}")

    if all_products:
        # Save in multiple formats
        csv_file = scraper.save_to_csv(all_products)
        json_file = scraper.save_to_json(all_products)

        # Generate report
        report = scraper.generate_report(all_products)

        print(f"\n=== SCRAPING COMPLETED ===")
        print(f"Total products: {report['total_products']}")
        print(f"CSV file: {csv_file}")
        print(f"JSON file: {json_file}")
        print(f"Categories found: {report['unique_categories']}")
        print(f"Brands found: {report['unique_brands']}")

        if report['top_categories']:
            print(f"Top categories: {', '.join([cat for cat, count in report['top_categories']])}")

        return {
            'status': 'success',
            'products_scraped': len(all_products),
            'files_created': [csv_file, json_file],
            'report': report
        }
    else:
        print("No products found. Check target URLs and selectors.")
        return {'status': 'no_data'}

if __name__ == "__main__":
    result = main()
    print(f"\nExecution result: {result['status']}")

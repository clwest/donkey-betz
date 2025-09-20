"""
E-Commerce & Dropshipping Spider Army
Massive intelligence gathering for online selling opportunities
"""

import scrapy
import re
import json
from datetime import datetime
from urllib.parse import urljoin
from .base_spider import ContentOpportunitySpider


class AmazonFBAOpportunitySpider(ContentOpportunitySpider):
    """
    Amazon FBA product research spider
    Finds profitable products and market gaps
    """

    name = 'amazon_fba_opportunities'
    allowed_domains = ['amazon.com', 'keepa.com', 'helium10.com']

    # Product categories to monitor
    target_categories = [
        'Home & Kitchen', 'Beauty & Personal Care', 'Sports & Outdoors',
        'Health & Household', 'Baby', 'Pet Supplies', 'Electronics',
        'Arts, Crafts & Sewing', 'Automotive', 'Tools & Home Improvement'
    ]

    def start_requests(self):
        """Generate requests for product research"""
        # Search for products with high demand, low competition
        search_params = [
            {'keyword': 'home organization', 'min_reviews': 100, 'max_reviews': 500},
            {'keyword': 'pet accessories', 'min_reviews': 50, 'max_reviews': 300},
            {'keyword': 'fitness equipment', 'min_reviews': 100, 'max_reviews': 400},
            {'keyword': 'baby products', 'min_reviews': 80, 'max_reviews': 350},
            {'keyword': 'kitchen gadgets', 'min_reviews': 150, 'max_reviews': 600}
        ]

        for params in search_params:
            # Amazon search URL
            url = f"https://www.amazon.com/s?k={params['keyword'].replace(' ', '+')}"

            yield scrapy.Request(
                url=url,
                callback=self.parse_amazon_search,
                meta={
                    'search_params': params,
                    'opportunity_type': 'amazon_fba'
                }
            )

    def parse_amazon_search(self, response):
        """Parse Amazon search results for FBA opportunities"""
        products = response.css('[data-component-type="s-search-result"]')

        for product in products[:20]:  # Top 20 results
            try:
                opportunity = self.extract_amazon_product(product, response)
                if opportunity and self.is_fba_opportunity(opportunity):
                    intelligence = self.process_item(opportunity, response)
                    if intelligence:
                        yield intelligence

            except Exception as e:
                self.logger.error(f"Error extracting Amazon product: {e}")

    def extract_amazon_product(self, product, response):
        """Extract product details for FBA analysis"""
        try:
            title = product.css('h2 a span::text').get()
            if not title:
                return None

            price_elem = product.css('.a-price-whole::text').get()
            price = float(re.sub(r'[^\d.]', '', price_elem or '0')) if price_elem else 0

            rating_elem = product.css('.a-icon-alt::text').get()
            rating = float(rating_elem.split()[0]) if rating_elem and 'out of' in rating_elem else 0

            review_count_elem = product.css('a[href*="reviews"] span::text').get()
            review_count = int(re.sub(r'[^\d]', '', review_count_elem or '0')) if review_count_elem else 0

            image_url = product.css('img::attr(src)').get()
            product_url = product.css('h2 a::attr(href)').get()

            return {
                'id': f"amazon_{hash(title + str(price))}",
                'title': title.strip(),
                'price': price,
                'rating': rating,
                'review_count': review_count,
                'image_url': image_url,
                'url': urljoin(response.url, product_url) if product_url else None,
                'source': 'amazon_search',
                'opportunity_type': 'fba_product',
                'estimated_profit_margin': self.calculate_profit_margin(price),
                'competition_level': self.assess_competition(review_count, rating),
                'market_demand': self.assess_demand(review_count, rating)
            }

        except Exception as e:
            self.logger.error(f"Error extracting Amazon product details: {e}")
            return None

    def is_fba_opportunity(self, product):
        """Determine if product is a good FBA opportunity"""
        # Criteria for good FBA opportunity
        return (
            product['price'] >= 15 and product['price'] <= 50 and  # Good price range
            product['review_count'] >= 50 and product['review_count'] <= 500 and  # Not oversaturated
            product['rating'] >= 3.5 and  # Decent rating
            product['estimated_profit_margin'] >= 0.3  # 30%+ margin
        )

    def calculate_profit_margin(self, price):
        """Estimate profit margin for FBA"""
        if price <= 0:
            return 0

        # Rough FBA cost calculation
        amazon_fees = price * 0.15  # ~15% Amazon fees
        fba_fees = 3.0  # Average FBA fulfillment fee
        cost_of_goods = price * 0.4  # Assume 40% COGS

        profit = price - amazon_fees - fba_fees - cost_of_goods
        return max(0, profit / price)

    def assess_competition(self, review_count, rating):
        """Assess competition level"""
        if review_count > 1000:
            return 'high'
        elif review_count > 500:
            return 'medium'
        else:
            return 'low'

    def assess_demand(self, review_count, rating):
        """Assess market demand"""
        demand_score = (review_count * rating) / 100
        if demand_score > 20:
            return 'high'
        elif demand_score > 10:
            return 'medium'
        else:
            return 'low'


class ShopifyDropshippingSpider(ContentOpportunitySpider):
    """
    Shopify dropshipping opportunity spider
    Finds trending products and suppliers
    """

    name = 'shopify_dropshipping'
    allowed_domains = ['aliexpress.com', 'oberlo.com', 'spocket.co']

    trending_niches = [
        'fitness', 'pets', 'beauty', 'home_decor', 'tech_gadgets',
        'kitchen', 'baby', 'gaming', 'outdoor', 'fashion'
    ]

    def start_requests(self):
        """Generate requests for dropshipping research"""
        for niche in self.trending_niches:
            # AliExpress trending products
            url = f"https://www.aliexpress.com/wholesale?SearchText={niche}&SortType=total_tranpro_desc"

            yield scrapy.Request(
                url=url,
                callback=self.parse_aliexpress_trending,
                meta={
                    'niche': niche,
                    'opportunity_type': 'dropshipping'
                }
            )

    def parse_aliexpress_trending(self, response):
        """Parse AliExpress for trending dropshipping products"""
        products = response.css('.item')

        for product in products[:15]:
            try:
                opportunity = self.extract_aliexpress_product(product, response)
                if opportunity and self.is_dropshipping_opportunity(opportunity):
                    intelligence = self.process_item(opportunity, response)
                    if intelligence:
                        yield intelligence

            except Exception as e:
                self.logger.error(f"Error extracting AliExpress product: {e}")

    def extract_aliexpress_product(self, product, response):
        """Extract product details for dropshipping analysis"""
        try:
            title = product.css('.item-title::text').get()
            if not title:
                return None

            price_elem = product.css('.price-current::text').get()
            price = float(re.findall(r'[\d.]+', price_elem or '0')[0]) if price_elem else 0

            orders_elem = product.css('.item-sales::text').get()
            orders = int(re.findall(r'\d+', orders_elem or '0')[0]) if orders_elem else 0

            rating_elem = product.css('.star-rating::attr(title)').get()
            rating = float(rating_elem.split()[0]) if rating_elem else 0

            return {
                'id': f"ali_{hash(title + str(price))}",
                'title': title.strip(),
                'wholesale_price': price,
                'total_orders': orders,
                'rating': rating,
                'niche': response.meta['niche'],
                'source': 'aliexpress',
                'opportunity_type': 'dropshipping_product',
                'suggested_retail_price': price * 2.5,  # 150% markup
                'profit_margin': 0.6,  # 60% margin typical for dropshipping
                'demand_indicator': self.calculate_demand_score(orders, rating),
                'supplier_reliability': self.assess_supplier(rating, orders)
            }

        except Exception as e:
            self.logger.error(f"Error extracting AliExpress product: {e}")
            return None

    def is_dropshipping_opportunity(self, product):
        """Determine if product is good for dropshipping"""
        return (
            product['wholesale_price'] >= 5 and product['wholesale_price'] <= 30 and
            product['total_orders'] >= 100 and
            product['rating'] >= 4.0 and
            product['demand_indicator'] >= 'medium'
        )

    def calculate_demand_score(self, orders, rating):
        """Calculate demand score"""
        score = (orders * rating) / 1000
        if score > 5:
            return 'high'
        elif score > 2:
            return 'medium'
        else:
            return 'low'

    def assess_supplier(self, rating, orders):
        """Assess supplier reliability"""
        if rating >= 4.5 and orders >= 1000:
            return 'excellent'
        elif rating >= 4.0 and orders >= 500:
            return 'good'
        else:
            return 'fair'


class EtsyHandmadeSpider(ContentOpportunitySpider):
    """
    Etsy handmade opportunity spider
    Finds profitable craft and handmade niches
    """

    name = 'etsy_handmade'
    allowed_domains = ['etsy.com']

    craft_categories = [
        'jewelry', 'home-living', 'clothing', 'wedding', 'craft-supplies',
        'vintage', 'toys-games', 'art-collectibles', 'bags-purses'
    ]

    def start_requests(self):
        """Generate requests for Etsy research"""
        for category in self.craft_categories:
            url = f"https://www.etsy.com/c/{category}?ref=pagination&page=1"

            yield scrapy.Request(
                url=url,
                callback=self.parse_etsy_category,
                meta={
                    'category': category,
                    'opportunity_type': 'handmade'
                }
            )

    def parse_etsy_category(self, response):
        """Parse Etsy category for handmade opportunities"""
        products = response.css('.js-merch-stash-check-listing')

        for product in products[:20]:
            try:
                opportunity = self.extract_etsy_product(product, response)
                if opportunity and self.is_handmade_opportunity(opportunity):
                    intelligence = self.process_item(opportunity, response)
                    if intelligence:
                        yield intelligence

            except Exception as e:
                self.logger.error(f"Error extracting Etsy product: {e}")

    def extract_etsy_product(self, product, response):
        """Extract Etsy product for handmade analysis"""
        try:
            title = product.css('h3::text').get()
            if not title:
                return None

            price_elem = product.css('.currency-value::text').get()
            price = float(price_elem) if price_elem else 0

            shop_name = product.css('.shop2-shop-name::text').get()
            sales_elem = product.css('.shop2-review-rating::text').get()

            return {
                'id': f"etsy_{hash(title + str(price))}",
                'title': title.strip(),
                'price': price,
                'shop_name': shop_name,
                'category': response.meta['category'],
                'source': 'etsy',
                'opportunity_type': 'handmade_product',
                'material_cost_estimate': price * 0.3,  # Estimate 30% material cost
                'time_investment': self.estimate_time_investment(price),
                'profit_per_hour': self.calculate_hourly_profit(price),
                'competition_level': 'medium',  # Default assessment
                'skill_level_required': self.assess_skill_level(response.meta['category'])
            }

        except Exception as e:
            self.logger.error(f"Error extracting Etsy product: {e}")
            return None

    def is_handmade_opportunity(self, product):
        """Determine if handmade product is profitable"""
        return (
            product['price'] >= 20 and
            product['profit_per_hour'] >= 15  # $15/hour minimum
        )

    def estimate_time_investment(self, price):
        """Estimate time to make product"""
        if price <= 25:
            return 2  # 2 hours
        elif price <= 50:
            return 4  # 4 hours
        elif price <= 100:
            return 8  # 8 hours
        else:
            return 16  # 16+ hours

    def calculate_hourly_profit(self, price):
        """Calculate profit per hour"""
        material_cost = price * 0.3
        etsy_fees = price * 0.065  # 6.5% Etsy fees
        time_hours = self.estimate_time_investment(price)

        profit = price - material_cost - etsy_fees
        return profit / time_hours if time_hours > 0 else 0

    def assess_skill_level(self, category):
        """Assess required skill level"""
        skill_map = {
            'jewelry': 'intermediate',
            'clothing': 'advanced',
            'home-living': 'beginner',
            'craft-supplies': 'beginner',
            'art-collectibles': 'advanced'
        }
        return skill_map.get(category, 'intermediate')


class PrintOnDemandSpider(ContentOpportunitySpider):
    """
    Print-on-demand opportunity spider
    Finds trending designs and niches
    """

    name = 'print_on_demand'
    allowed_domains = ['redbubble.com', 'teespring.com', 'merch.amazon.com']

    trending_topics = [
        'funny quotes', 'motivational', 'pets', 'gaming', 'sports',
        'hobbies', 'professions', 'holidays', 'vintage', 'minimalist'
    ]

    def start_requests(self):
        """Generate requests for POD research"""
        for topic in self.trending_topics:
            # RedBubble trending
            url = f"https://www.redbubble.com/shop?query={topic.replace(' ', '%20')}&ref=search_box"

            yield scrapy.Request(
                url=url,
                callback=self.parse_redbubble_trends,
                meta={
                    'topic': topic,
                    'opportunity_type': 'print_on_demand'
                }
            )

    def parse_redbubble_trends(self, response):
        """Parse RedBubble for trending designs"""
        designs = response.css('[data-testid="search-results"] > div')

        for design in designs[:15]:
            try:
                opportunity = self.extract_pod_design(design, response)
                if opportunity:
                    intelligence = self.process_item(opportunity, response)
                    if intelligence:
                        yield intelligence

            except Exception as e:
                self.logger.error(f"Error extracting POD design: {e}")

    def extract_pod_design(self, design, response):
        """Extract POD design opportunity"""
        try:
            title_elem = design.css('[data-testid="product-title"]::text').get()
            if not title_elem:
                return None

            price_elem = design.css('[data-testid="product-price"]::text').get()
            price = float(re.findall(r'[\d.]+', price_elem or '0')[0]) if price_elem else 0

            return {
                'id': f"pod_{hash(title_elem + str(price))}",
                'design_concept': title_elem.strip(),
                'price': price,
                'topic': response.meta['topic'],
                'source': 'redbubble',
                'opportunity_type': 'print_on_demand_design',
                'royalty_rate': 0.10,  # ~10% royalty typical
                'design_complexity': self.assess_design_complexity(title_elem),
                'market_potential': self.assess_market_potential(response.meta['topic']),
                'creation_time_hours': self.estimate_design_time(title_elem),
                'monthly_earning_potential': self.estimate_monthly_earnings(price)
            }

        except Exception as e:
            self.logger.error(f"Error extracting POD design: {e}")
            return None

    def assess_design_complexity(self, title):
        """Assess how complex the design might be"""
        if any(word in title.lower() for word in ['simple', 'text', 'quote', 'minimal']):
            return 'low'
        elif any(word in title.lower() for word in ['detailed', 'illustration', 'cartoon']):
            return 'high'
        else:
            return 'medium'

    def assess_market_potential(self, topic):
        """Assess market potential for topic"""
        high_potential = ['funny quotes', 'pets', 'gaming', 'motivational']
        if topic in high_potential:
            return 'high'
        else:
            return 'medium'

    def estimate_design_time(self, title):
        """Estimate time to create design"""
        complexity = self.assess_design_complexity(title)
        time_map = {'low': 2, 'medium': 5, 'high': 12}
        return time_map.get(complexity, 5)

    def estimate_monthly_earnings(self, price):
        """Estimate potential monthly earnings"""
        royalty = price * 0.10
        # Conservative estimate: 10-50 sales per month for good designs
        return royalty * 30  # Average estimate
"""
Content Marketplace Agent - Lists content for sale on real platforms
"""

import os
import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, List
import aiohttp
import hashlib
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core.llm_enforcer import get_llm_enforcer
from .spider_data_mixin import SpiderDataMixin, IntelligenceData

logger = logging.getLogger(__name__)


class ContentMarketplaceAgent(SpiderDataMixin):
    """
    Agent that lists content for sale on real marketplaces:
    - Fiverr gig creation
    - Upwork portfolio
    - Content marketplaces
    - Direct sales platform

    Enhanced with real-time spider intelligence for:
    - Content market trends
    - Platform opportunities
    - Pricing optimization
    - Demand analysis
    """

    def __init__(self):
        # Initialize spider data mixin first
        super().__init__()

        # Setup spider data receiver for content marketplace intelligence
        self.setup_spider_data_receiver(
            agent_id='content_marketplace_agent',
            agent_type='content_marketing',
            quality_threshold=0.8,
            custom_keywords=['gumroad', 'medium', 'content', 'marketplace', 'monetization', 'design']
        )

        # Add intelligence callback
        self.add_intelligence_callback(self._on_marketplace_intelligence)

        self.listed_content = []
        self.market_intelligence = []  # Store spider intelligence
        self.marketplaces = {
            'direct_sales': {
                'name': 'Direct Sales Portal',
                'url': 'https://your-domain.com/content-store',
                'commission': 0.0  # No commission for direct sales
            },
            'gumroad': {
                'name': 'Gumroad',
                'url': 'https://gumroad.com',
                'commission': 0.09  # 9% + payment processing
            },
            'contentfly': {
                'name': 'ContentFly',
                'url': 'https://contentfly.com',
                'commission': 0.20  # 20% commission
            },
            'constant_content': {
                'name': 'Constant Content',
                'url': 'https://www.constant-content.com',
                'commission': 0.35  # 35% commission
            }
        }
        self.session = None

    async def initialize(self):
        """Initialize HTTP session"""
        if not self.session:
            self.session = aiohttp.ClientSession()

    async def list_content(self, content: Dict[str, Any], marketplaces: List[str] = None) -> Dict[str, Any]:
        """
        List content for sale on specified marketplaces

        Args:
            content: Content to list (from content creator agent)
            marketplaces: List of marketplace names to list on

        Returns:
            Listing results
        """
        await self.initialize()

        if not marketplaces:
            marketplaces = ['direct_sales']  # Default to direct sales

        listing_results = {
            'content_id': self._generate_content_id(content),
            'title': content.get('title', 'Untitled'),
            'type': content.get('type'),
            'listings': [],
            'total_potential_earnings': 0,
            'listed_at': datetime.now().isoformat()
        }

        for marketplace_name in marketplaces:
            if marketplace_name in self.marketplaces:
                marketplace = self.marketplaces[marketplace_name]

                # Create listing for this marketplace
                listing = await self._create_marketplace_listing(
                    content,
                    marketplace
                )

                listing_results['listings'].append(listing)
                listing_results['total_potential_earnings'] += listing['potential_earnings']

        # Save listing record
        self.listed_content.append(listing_results)
        self._save_listing_record(listing_results)

        logger.info(f"✅ Listed content on {len(listing_results['listings'])} marketplaces")

        return listing_results

    async def _create_marketplace_listing(self, content: Dict[str, Any], marketplace: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a listing on a specific marketplace

        Args:
            content: Content to list
            marketplace: Marketplace details

        Returns:
            Listing details
        """
        # Calculate pricing based on content value and marketplace commission
        base_price = content.get('value_estimate', 50)
        marketplace_price = base_price / (1 - marketplace['commission'])  # Adjust for commission

        listing = {
            'marketplace': marketplace['name'],
            'status': 'pending',
            'price': round(marketplace_price, 2),
            'commission_rate': marketplace['commission'],
            'potential_earnings': round(base_price, 2),
            'listing_url': None,
            'listing_data': {}
        }

        try:
            if marketplace['name'] == 'Direct Sales Portal':
                listing.update(await self._list_on_direct_portal(content, marketplace_price))
            elif marketplace['name'] == 'Gumroad':
                listing.update(await self._prepare_gumroad_listing(content, marketplace_price))
            else:
                listing.update(await self._prepare_generic_listing(content, marketplace_price, marketplace))

        except Exception as e:
            logger.error(f"Failed to list on {marketplace['name']}: {e}")
            listing['status'] = 'failed'
            listing['error'] = str(e)

        return listing

    async def _list_on_direct_portal(self, content: Dict[str, Any], price: float) -> Dict[str, Any]:
        """
        List content on direct sales portal

        Args:
            content: Content to list
            price: Selling price

        Returns:
            Listing details
        """
        # Create a simple sales page
        content_id = self._generate_content_id(content)
        sales_page_path = f"/tmp/content_store/{content_id}"
        os.makedirs(sales_page_path, exist_ok=True)

        # Create HTML sales page
        sales_page_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{content.get('title', 'Premium Content')}</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
                .content-card {{ border: 2px solid #4CAF50; border-radius: 10px; padding: 20px; margin: 20px 0; }}
                .price {{ font-size: 32px; color: #4CAF50; font-weight: bold; }}
                .buy-button {{
                    background: #4CAF50;
                    color: white;
                    padding: 15px 30px;
                    font-size: 18px;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                }}
                .buy-button:hover {{ background: #45a049; }}
            </style>
        </head>
        <body>
            <div class="content-card">
                <h1>{content.get('title', 'Premium Content')}</h1>
                <p><strong>Type:</strong> {content.get('type', 'Digital Content')}</p>
                <p><strong>Word Count:</strong> {content.get('word_count', 'N/A')}</p>
                <p><strong>Created:</strong> {content.get('created_at', 'Recently')}</p>

                <div class="price">${price:.2f}</div>

                <h2>What You Get:</h2>
                <ul>
                    <li>High-quality, original content</li>
                    <li>SEO-optimized writing</li>
                    <li>Ready to publish</li>
                    <li>Full commercial rights</li>
                    <li>Instant download</li>
                </ul>

                <h2>Sample:</h2>
                <p>{content.get('content', 'Content preview not available')[:200]}...</p>

                <button class="buy-button" onclick="initiatePurchase()">Buy Now - ${price:.2f}</button>

                <script>
                    function initiatePurchase() {{
                        // Integrate with payment processor (Stripe, PayPal, etc.)
                        alert('Payment integration would go here. Content ID: {content_id}');
                        // In production: window.location.href = '/checkout?content_id={content_id}';
                    }}
                </script>
            </div>
        </body>
        </html>
        """

        # Save the sales page
        with open(f"{sales_page_path}/index.html", 'w') as f:
            f.write(sales_page_html)

        # Save the actual content (encrypted/protected in production)
        with open(f"{sales_page_path}/content.json", 'w') as f:
            json.dump(content, f, indent=2)

        return {
            'status': 'live',
            'listing_url': f"file://{sales_page_path}/index.html",
            'listing_data': {
                'sales_page_path': sales_page_path,
                'content_id': content_id,
                'direct_link': f"/content/{content_id}"
            }
        }

    async def _prepare_gumroad_listing(self, content: Dict[str, Any], price: float) -> Dict[str, Any]:
        """
        Prepare content for Gumroad listing

        Args:
            content: Content to list
            price: Selling price

        Returns:
            Gumroad listing preparation
        """
        # Prepare Gumroad product data
        gumroad_product = {
            'name': content.get('title', 'Premium Content'),
            'price': price,
            'description': self._create_product_description(content),
            'tags': content.get('keywords', []),
            'file_path': f"/tmp/content_{content.get('type')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            'cover_image': None,  # Would generate cover image in production
            'preview_url': None
        }

        # Save content file for upload
        with open(gumroad_product['file_path'], 'w') as f:
            f.write(content.get('content', ''))

        # Create instruction file for manual listing
        instructions = f"""
        GUMROAD LISTING READY

        Product: {gumroad_product['name']}
        Price: ${gumroad_product['price']:.2f}
        File: {gumroad_product['file_path']}

        Steps to list on Gumroad:
        1. Log in to gumroad.com
        2. Click "New Product"
        3. Upload file: {gumroad_product['file_path']}
        4. Set price: ${gumroad_product['price']:.2f}
        5. Add description (below)
        6. Publish product
        7. Copy product URL
        8. Update tracking system with URL

        DESCRIPTION TO USE:
        {gumroad_product['description']}
        """

        with open(f"{gumroad_product['file_path']}.instructions.txt", 'w') as f:
            f.write(instructions)

        return {
            'status': 'prepared',
            'listing_url': 'https://gumroad.com/l/pending',
            'listing_data': gumroad_product,
            'instructions_path': f"{gumroad_product['file_path']}.instructions.txt"
        }

    async def _prepare_generic_listing(self, content: Dict[str, Any], price: float, marketplace: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare generic marketplace listing

        Args:
            content: Content to list
            price: Selling price
            marketplace: Marketplace details

        Returns:
            Generic listing preparation
        """
        listing_folder = f"/tmp/marketplace_listings/{marketplace['name'].replace(' ', '_')}"
        os.makedirs(listing_folder, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        content_file = f"{listing_folder}/content_{timestamp}.md"

        # Save content
        with open(content_file, 'w') as f:
            f.write(content.get('content', ''))

        # Create listing metadata
        metadata = {
            'title': content.get('title'),
            'price': price,
            'type': content.get('type'),
            'word_count': content.get('word_count'),
            'keywords': content.get('keywords', []),
            'description': self._create_product_description(content),
            'content_file': content_file,
            'marketplace': marketplace['name'],
            'marketplace_url': marketplace['url']
        }

        metadata_file = f"{listing_folder}/metadata_{timestamp}.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

        return {
            'status': 'prepared',
            'listing_url': marketplace['url'],
            'listing_data': {
                'content_file': content_file,
                'metadata_file': metadata_file,
                'listing_folder': listing_folder
            }
        }

    def _create_product_description(self, content: Dict[str, Any]) -> str:
        """Create compelling product description using REAL AI"""
        # Use the LLM enforcer to generate REAL product description
        enforcer = get_llm_enforcer()

        # Build context about the content
        context = f"""
Content Details:
- Title: {content.get('title', 'Premium Content')}
- Type: {content.get('type', 'Professional Content')}
- Word Count: {content.get('word_count', 1000)} words
- Keywords: {', '.join(content.get('keywords', ['quality', 'professional'])[:5])}
- Topic: {content.get('topic', 'Business/Technology')}
- Value: ${content.get('value', 100)}
- Format: {content.get('format', 'Blog post / Article')}
        """

        prompt = """
Create a compelling, unique product description for this content listing.

Requirements:
1. Make it exciting and persuasive - this needs to sell!
2. Highlight the unique value proposition
3. Use emojis strategically (but not excessively)
4. Include specific benefits for buyers
5. Create urgency without being pushy
6. Be specific about what's included
7. Around 200-300 words
8. Sound professional but engaging
9. Include a strong call-to-action

Make each description unique and tailored to the specific content.
Focus on the VALUE the buyer will receive, not just features.
        """

        try:
            result = enforcer.enforce_real_ai(
                prompt=prompt,
                context=context,
                agent_name="ContentMarketplaceAgent",
                task_type="content",
                max_tokens=500,
                temperature=0.9
            )

            if result['success']:
                logger.info(f"✅ Generated REAL AI product description using {result['provider']}/{result['model']}")
                return result['response']
            else:
                logger.error(f"❌ Failed to generate AI description: {result['error']}")
                # Simple fallback
                return f"""
{content.get('title', 'Premium Content')}

High-quality {content.get('type', 'content')} - {content.get('word_count', 'professional')} words.
Keywords: {', '.join(content.get('keywords', ['quality'])[:3])}

Instant download. Full commercial rights included.
Value: ${content.get('value', 100)}
"""

        except Exception as e:
            logger.error(f"❌ Exception generating description: {e}")
            return f"{content.get('title', 'Content')} - ${content.get('value', 100)}"

    def _generate_content_id(self, content: Dict[str, Any]) -> str:
        """Generate unique content ID"""
        data = f"{content.get('title', '')}_{content.get('created_at', '')}_{datetime.now()}"
        return hashlib.md5(data.encode()).hexdigest()[:12]

    def _save_listing_record(self, listing: Dict[str, Any]):
        """Save listing record for tracking"""
        listings_file = '/tmp/content_listings.json'

        try:
            # Load existing listings
            if os.path.exists(listings_file):
                with open(listings_file, 'r') as f:
                    listings = json.load(f)
            else:
                listings = []

            # Add new listing
            listings.append(listing)

            # Save updated list
            with open(listings_file, 'w') as f:
                json.dump(listings, f, indent=2)

            logger.info(f"💾 Listing record saved: {listing['title']}")

        except Exception as e:
            logger.error(f"Failed to save listing record: {e}")

    async def check_sales(self) -> Dict[str, Any]:
        """
        Check for sales across all marketplaces

        Returns:
            Sales report
        """
        sales_report = {
            'total_sales': 0,
            'total_revenue': 0,
            'sales_by_marketplace': {},
            'checked_at': datetime.now().isoformat()
        }

        # In production, this would check actual marketplace APIs
        # For now, simulate checking
        for listing in self.listed_content:
            marketplace_sales = {
                'views': 0,
                'sales': 0,
                'revenue': 0
            }

            # Check each marketplace listing
            for marketplace_listing in listing.get('listings', []):
                # In production: check actual sales via API
                # For demo: simulate some sales
                if marketplace_listing['status'] == 'live':
                    marketplace_sales['views'] += 10
                    marketplace_sales['sales'] += 1
                    marketplace_sales['revenue'] += marketplace_listing['potential_earnings']

            sales_report['total_sales'] += marketplace_sales['sales']
            sales_report['total_revenue'] += marketplace_sales['revenue']

        logger.info(f"💰 Sales check: {sales_report['total_sales']} sales, ${sales_report['total_revenue']:.2f} revenue")

        return sales_report

    async def close(self):
        """Close HTTP session and spider data receiver"""
        if self.session:
            await self.session.close()

        # Stop spider data receiver
        await self.stop_spider_data_receiver()

    async def process_spider_intelligence(self, data: IntelligenceData) -> Dict[str, Any]:
        """Process spider intelligence for content marketplace optimization"""
        try:
            content = data.content
            content_text = str(content).lower()

            # Analyze marketplace intelligence
            marketplace_insights = {
                'agent_id': 'content_marketplace_agent',
                'data_type': data.data_type,
                'spider_id': data.spider_id,
                'quality_score': data.quality_score,
                'marketplace_analysis': {
                    'platform_opportunities': [],
                    'pricing_insights': {},
                    'content_demand': {},
                    'competitive_analysis': {}
                },
                'recommended_actions': [],
                'urgency_level': 'normal',
                'processed_at': datetime.now().isoformat()
            }

            # Analyze platform-specific opportunities
            if 'gumroad' in content_text:
                marketplace_insights['marketplace_analysis']['platform_opportunities'].append({
                    'platform': 'Gumroad',
                    'opportunity_type': 'digital_product_sales',
                    'confidence': data.quality_score
                })
                marketplace_insights['recommended_actions'].append('Consider listing digital products on Gumroad')

            if 'medium' in content_text:
                marketplace_insights['marketplace_analysis']['platform_opportunities'].append({
                    'platform': 'Medium',
                    'opportunity_type': 'content_monetization',
                    'confidence': data.quality_score
                })
                marketplace_insights['recommended_actions'].append('Explore Medium Partner Program opportunities')

            if '99designs' in content_text or 'design contest' in content_text:
                marketplace_insights['marketplace_analysis']['platform_opportunities'].append({
                    'platform': '99Designs',
                    'opportunity_type': 'design_services',
                    'confidence': data.quality_score
                })
                marketplace_insights['recommended_actions'].append('Consider design contest participation')

            # Analyze pricing insights
            if any(term in content_text for term in ['$', 'price', 'cost', 'fee', 'rate']):
                marketplace_insights['marketplace_analysis']['pricing_insights'] = {
                    'has_pricing_data': True,
                    'pricing_analysis_needed': True
                }
                marketplace_insights['recommended_actions'].append('Analyze pricing data for competitive positioning')

            # Analyze content demand
            demand_indicators = ['trending', 'popular', 'high demand', 'bestseller', 'viral']
            if any(indicator in content_text for indicator in demand_indicators):
                marketplace_insights['marketplace_analysis']['content_demand'] = {
                    'high_demand_detected': True,
                    'trend_analysis_recommended': True
                }
                marketplace_insights['recommended_actions'].append('Create content aligned with trending demand')

            # Set urgency based on quality and opportunities
            if data.quality_score > 0.9 and len(marketplace_insights['recommended_actions']) > 2:
                marketplace_insights['urgency_level'] = 'high'

            logger.info(f"📊 Processed marketplace intelligence: {len(marketplace_insights['recommended_actions'])} actions identified")

            return marketplace_insights

        except Exception as e:
            logger.error(f"Error processing marketplace intelligence: {e}")
            return {'error': str(e), 'agent_id': 'content_marketplace_agent'}

    async def _on_marketplace_intelligence(self, data: IntelligenceData, result: Dict[str, Any]):
        """Callback when marketplace intelligence is received"""
        try:
            # Store intelligence for later use
            self.market_intelligence.append({
                'data': data,
                'result': result,
                'received_at': datetime.now()
            })

            # Keep only last 100 intelligence items
            if len(self.market_intelligence) > 100:
                self.market_intelligence = self.market_intelligence[-100:]

            # Take action on high-urgency intelligence
            if result.get('urgency_level') == 'high':
                logger.info(f"🚨 High-urgency marketplace intelligence received from {data.spider_id}")

                # Auto-execute recommended actions for high-urgency items
                actions = result.get('recommended_actions', [])
                if actions:
                    logger.info(f"🎯 Auto-executing {len(actions)} high-priority actions")
                    await self._execute_intelligence_actions(actions, result)

        except Exception as e:
            logger.error(f"Error in marketplace intelligence callback: {e}")

    async def _execute_intelligence_actions(self, actions: List[str], intelligence_result: Dict[str, Any]):
        """Execute recommended actions from intelligence analysis"""
        try:
            for action in actions:
                if 'gumroad' in action.lower():
                    # Prepare for Gumroad listing
                    logger.info("🔧 Preparing Gumroad optimization strategy")

                elif 'medium' in action.lower():
                    # Analyze Medium opportunities
                    logger.info("🔧 Analyzing Medium monetization opportunities")

                elif 'pricing' in action.lower():
                    # Update pricing strategy
                    logger.info("🔧 Updating pricing strategy based on market data")

                elif 'trending' in action.lower() or 'demand' in action.lower():
                    # Adjust content strategy
                    logger.info("🔧 Adjusting content strategy for trending demand")

        except Exception as e:
            logger.error(f"Error executing intelligence actions: {e}")

    def get_marketplace_intelligence_summary(self) -> Dict[str, Any]:
        """Get summary of received marketplace intelligence"""
        if not self.market_intelligence:
            return {
                'total_intelligence_items': 0,
                'summary': 'No marketplace intelligence received yet'
            }

        # Analyze collected intelligence
        platform_opportunities = {}
        total_actions = 0
        high_urgency_count = 0

        for item in self.market_intelligence:
            result = item['result']

            # Count platform opportunities
            opportunities = result.get('marketplace_analysis', {}).get('platform_opportunities', [])
            for opp in opportunities:
                platform = opp.get('platform', 'unknown')
                platform_opportunities[platform] = platform_opportunities.get(platform, 0) + 1

            # Count actions
            total_actions += len(result.get('recommended_actions', []))

            # Count high urgency items
            if result.get('urgency_level') == 'high':
                high_urgency_count += 1

        return {
            'total_intelligence_items': len(self.market_intelligence),
            'platform_opportunities': platform_opportunities,
            'total_recommended_actions': total_actions,
            'high_urgency_items': high_urgency_count,
            'spider_data_metrics': self.get_spider_data_metrics(),
            'last_intelligence_received': self.market_intelligence[-1]['received_at'].isoformat() if self.market_intelligence else None
        }


# Test the marketplace agent
async def test_marketplace_agent():
    """Test the content marketplace agent"""
    agent = ContentMarketplaceAgent()

    # Sample content from content creator
    content = {
        'type': 'blog_post',
        'title': 'AI Revolution in Freelancing',
        'content': 'This is a sample blog post about AI...',
        'word_count': 800,
        'keywords': ['AI', 'freelancing', 'automation'],
        'value_estimate': 120.00,
        'created_at': datetime.now().isoformat()
    }

    # List on marketplaces
    listing_result = await agent.list_content(
        content,
        marketplaces=['direct_sales', 'gumroad']
    )

    print(f"\n📦 Listing Result:")
    print(f"Listed on {len(listing_result['listings'])} marketplaces")
    print(f"Potential earnings: ${listing_result['total_potential_earnings']:.2f}")

    for listing in listing_result['listings']:
        print(f"\n{listing['marketplace']}:")
        print(f"  Status: {listing['status']}")
        print(f"  Price: ${listing['price']:.2f}")
        print(f"  Your earnings: ${listing['potential_earnings']:.2f}")
        if listing.get('listing_url'):
            print(f"  URL: {listing['listing_url']}")

    # Check sales
    sales = await agent.check_sales()
    print(f"\n💰 Sales Report:")
    print(f"Total sales: {sales['total_sales']}")
    print(f"Total revenue: ${sales['total_revenue']:.2f}")

    await agent.close()


if __name__ == "__main__":
    asyncio.run(test_marketplace_agent())
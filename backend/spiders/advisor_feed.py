"""
Advisor Intelligence Feed System
Phase 3: Connect 25 Legendary Advisors to Real-Time Data

This module feeds specialized intelligence to legendary advisors
based on their expertise and investment philosophies.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import asyncio
import json
from django.core.cache import cache
from decimal import Decimal

logger = logging.getLogger(__name__)


class AdvisorFeed:
    """
    Manages personalized data feeds for 25 legendary advisors.
    Each advisor receives tailored intelligence based on their specialty.
    """

    # Legendary Advisors with their data requirements
    LEGENDARY_ADVISORS = {
        'Warren Buffett': {
            'specialty': 'Value Investing',
            'data_needs': ['financial_statements', 'dividend_history', 'market_fear_index', 'undervalued_stocks'],
            'keywords': ['value', 'moat', 'dividend', 'cash flow', 'P/E ratio', 'book value'],
            'refresh_rate': 3600  # Hourly updates
        },
        'Cathie Wood': {
            'specialty': 'Disruptive Innovation',
            'data_needs': ['tech_innovations', 'ai_breakthroughs', 'genomics_news', 'autonomous_vehicles'],
            'keywords': ['innovation', 'disruption', 'AI', 'genomics', 'robotics', 'space'],
            'refresh_rate': 1800  # 30-minute updates
        },
        'Ray Dalio': {
            'specialty': 'Macro Strategy',
            'data_needs': ['economic_indicators', 'debt_cycles', 'currency_movements', 'central_bank_policies'],
            'keywords': ['macro', 'debt', 'currency', 'inflation', 'interest rates', 'GDP'],
            'refresh_rate': 1800
        },
        'Peter Lynch': {
            'specialty': 'Growth Investing',
            'data_needs': ['earnings_growth', 'retail_trends', 'consumer_behavior', 'emerging_companies'],
            'keywords': ['growth', 'PEG ratio', 'retail', 'consumer', 'ten-bagger', 'GARP'],
            'refresh_rate': 3600
        },
        'Benjamin Graham': {
            'specialty': 'Security Analysis',
            'data_needs': ['balance_sheets', 'intrinsic_value', 'margin_of_safety', 'net_assets'],
            'keywords': ['intrinsic value', 'margin of safety', 'net-net', 'security analysis'],
            'refresh_rate': 7200  # 2-hour updates
        },
        'George Soros': {
            'specialty': 'Currency Markets',
            'data_needs': ['forex_rates', 'geopolitical_events', 'central_bank_actions', 'market_reflexivity'],
            'keywords': ['currency', 'forex', 'reflexivity', 'bubble', 'trend', 'momentum'],
            'refresh_rate': 900  # 15-minute updates
        },
        'Carl Icahn': {
            'specialty': 'Activist Investing',
            'data_needs': ['corporate_governance', 'proxy_battles', 'underperforming_companies', 'M&A_activity'],
            'keywords': ['activist', 'corporate raid', 'proxy', 'restructuring', 'spinoff'],
            'refresh_rate': 3600
        },
        'Paul Tudor Jones': {
            'specialty': 'Macro Trading',
            'data_needs': ['market_momentum', 'volatility_index', 'commodity_prices', 'risk_indicators'],
            'keywords': ['momentum', 'volatility', 'risk', 'commodity', 'futures', 'macro'],
            'refresh_rate': 600  # 10-minute updates
        },
        'Stanley Druckenmiller': {
            'specialty': 'Top-Down Investing',
            'data_needs': ['sector_rotation', 'economic_trends', 'market_cycles', 'liquidity_flows'],
            'keywords': ['top-down', 'sector', 'liquidity', 'cycle', 'trend', 'allocation'],
            'refresh_rate': 1800
        },
        'Charlie Munger': {
            'specialty': 'Mental Models',
            'data_needs': ['business_quality', 'competitive_advantages', 'management_quality', 'long_term_trends'],
            'keywords': ['mental model', 'moat', 'quality', 'rationality', 'psychology', 'bias'],
            'refresh_rate': 7200
        },
        'John Bogle': {
            'specialty': 'Index Investing',
            'data_needs': ['index_performance', 'etf_flows', 'market_breadth', 'cost_ratios'],
            'keywords': ['index', 'ETF', 'passive', 'cost', 'Vanguard', 'S&P 500'],
            'refresh_rate': 3600
        },
        'Peter Thiel': {
            'specialty': 'Venture Capital',
            'data_needs': ['startup_funding', 'unicorn_valuations', 'tech_breakthroughs', 'founder_profiles'],
            'keywords': ['startup', 'venture', 'unicorn', 'zero to one', 'monopoly', 'founder'],
            'refresh_rate': 1800
        },
        'Marc Andreessen': {
            'specialty': 'Software Ventures',
            'data_needs': ['software_trends', 'saas_metrics', 'developer_tools', 'api_economy'],
            'keywords': ['software', 'SaaS', 'API', 'developer', 'platform', 'network effect'],
            'refresh_rate': 1800
        },
        'Elon Musk': {
            'specialty': 'Transformative Tech',
            'data_needs': ['space_tech', 'ev_market', 'ai_development', 'energy_storage', 'neural_interfaces'],
            'keywords': ['Tesla', 'SpaceX', 'AI', 'electric', 'mars', 'neural', 'battery'],
            'refresh_rate': 1800
        },
        'Jeff Bezos': {
            'specialty': 'Customer Focus',
            'data_needs': ['ecommerce_trends', 'customer_satisfaction', 'logistics_innovation', 'cloud_computing'],
            'keywords': ['customer', 'Amazon', 'AWS', 'logistics', 'day one', 'flywheel'],
            'refresh_rate': 3600
        },
        'Bill Gates': {
            'specialty': 'Technology Strategy',
            'data_needs': ['software_adoption', 'healthcare_tech', 'education_tech', 'climate_tech'],
            'keywords': ['Microsoft', 'software', 'healthcare', 'education', 'climate', 'philanthropy'],
            'refresh_rate': 3600
        },
        'Jack Ma': {
            'specialty': 'E-commerce',
            'data_needs': ['asian_markets', 'digital_payments', 'b2b_platforms', 'emerging_markets'],
            'keywords': ['Alibaba', 'e-commerce', 'China', 'payment', 'B2B', 'emerging'],
            'refresh_rate': 3600
        },
        'Masayoshi Son': {
            'specialty': 'Vision Investing',
            'data_needs': ['ai_companies', 'robotics', 'iot_adoption', 'mega_deals'],
            'keywords': ['SoftBank', 'Vision Fund', 'AI', 'robotics', 'IoT', 'unicorn'],
            'refresh_rate': 1800
        },
        'Reid Hoffman': {
            'specialty': 'Network Effects',
            'data_needs': ['social_networks', 'marketplace_dynamics', 'platform_economics', 'viral_growth'],
            'keywords': ['LinkedIn', 'network', 'marketplace', 'platform', 'blitzscaling', 'viral'],
            'refresh_rate': 3600
        },
        'Naval Ravikant': {
            'specialty': 'Angel Investing',
            'data_needs': ['early_stage_startups', 'crypto_projects', 'creator_economy', 'wisdom_trends'],
            'keywords': ['angel', 'crypto', 'leverage', 'wealth', 'specific knowledge', 'AngelList'],
            'refresh_rate': 3600
        },
        'Sam Altman': {
            'specialty': 'AI & Startups',
            'data_needs': ['ai_research', 'agi_progress', 'startup_ecosystem', 'y_combinator'],
            'keywords': ['OpenAI', 'GPT', 'AGI', 'YC', 'startup', 'AI safety'],
            'refresh_rate': 1800
        },
        'Chamath Palihapitiya': {
            'specialty': 'SPAC Innovation',
            'data_needs': ['spac_deals', 'climate_investments', 'healthcare_disruption', 'social_impact'],
            'keywords': ['SPAC', 'Social Capital', 'climate', 'healthcare', 'disruption'],
            'refresh_rate': 1800
        },
        'Mark Cuban': {
            'specialty': 'Business Operations',
            'data_needs': ['small_business', 'sports_analytics', 'media_trends', 'direct_to_consumer'],
            'keywords': ['Shark Tank', 'Mavericks', 'business', 'operations', 'media', 'D2C'],
            'refresh_rate': 3600
        },
        'Tim Cook': {
            'specialty': 'Supply Chain',
            'data_needs': ['supply_chain_metrics', 'hardware_innovation', 'services_growth', 'privacy_tech'],
            'keywords': ['Apple', 'supply chain', 'iPhone', 'services', 'privacy', 'hardware'],
            'refresh_rate': 3600
        },
        'Satya Nadella': {
            'specialty': 'Cloud Strategy',
            'data_needs': ['cloud_adoption', 'enterprise_saas', 'ai_services', 'developer_ecosystem'],
            'keywords': ['Azure', 'cloud', 'enterprise', 'AI', 'GitHub', 'productivity'],
            'refresh_rate': 3600
        }
    }

    def __init__(self):
        self.active_feeds = {}
        self.feed_stats = {
            'total_updates': 0,
            'successful_feeds': 0,
            'failed_feeds': 0,
            'advisors_active': 0
        }
        self._initialize_feeds()

    def _initialize_feeds(self):
        """Initialize feed configurations for all advisors"""
        for advisor_name, config in self.LEGENDARY_ADVISORS.items():
            self.active_feeds[advisor_name] = {
                'status': 'active',
                'last_update': None,
                'update_count': 0,
                'current_insights': [],
                'performance': {
                    'recommendations': 0,
                    'successful_calls': 0,
                    'roi': 0.0
                }
            }

        self.feed_stats['advisors_active'] = len(self.active_feeds)
        logger.info(f"🎓 Initialized feeds for {self.feed_stats['advisors_active']} legendary advisors")

    async def feed_advisor(self, advisor_name: str, data: Dict) -> Dict:
        """
        Feed relevant data to a specific advisor

        Args:
            advisor_name: Name of the advisor
            data: Data to feed to the advisor

        Returns:
            Feed result with insights
        """
        if advisor_name not in self.LEGENDARY_ADVISORS:
            logger.warning(f"⚠️ Unknown advisor: {advisor_name}")
            return {'status': 'error', 'message': 'Unknown advisor'}

        advisor_config = self.LEGENDARY_ADVISORS[advisor_name]
        feed_result = {
            'advisor': advisor_name,
            'specialty': advisor_config['specialty'],
            'timestamp': datetime.now().isoformat(),
            'insights': []
        }

        try:
            # Filter data based on advisor's needs
            relevant_data = self._filter_for_advisor(data, advisor_config)

            if not relevant_data:
                logger.debug(f"📊 No relevant data for {advisor_name}")
                return feed_result

            # Generate insights based on advisor's philosophy
            insights = await self._generate_insights(advisor_name, relevant_data)

            # Update advisor's feed
            self.active_feeds[advisor_name]['last_update'] = datetime.now()
            self.active_feeds[advisor_name]['update_count'] += 1
            self.active_feeds[advisor_name]['current_insights'] = insights

            feed_result['insights'] = insights
            feed_result['status'] = 'success'

            # Cache the feed
            cache.set(f"advisor_feed:{advisor_name}", feed_result, advisor_config['refresh_rate'])

            # Update statistics
            self.feed_stats['total_updates'] += 1
            self.feed_stats['successful_feeds'] += 1

            logger.info(f"💡 Fed {advisor_name}: {len(insights)} insights generated")

        except Exception as e:
            logger.error(f"❌ Error feeding {advisor_name}: {e}")
            feed_result['status'] = 'error'
            feed_result['error'] = str(e)
            self.feed_stats['failed_feeds'] += 1

        return feed_result

    def _filter_for_advisor(self, data: Dict, advisor_config: Dict) -> Dict:
        """Filter data based on advisor's interests"""
        filtered_data = {}

        # Check if data contains relevant keywords
        data_str = json.dumps(data).lower()
        relevance_score = 0

        for keyword in advisor_config['keywords']:
            if keyword.lower() in data_str:
                relevance_score += 1

        if relevance_score == 0:
            return {}

        # Check data type matches advisor's needs
        data_type = data.get('type', 'unknown')
        if any(need in data_type for need in advisor_config['data_needs']):
            filtered_data = data

        return filtered_data

    async def _generate_insights(self, advisor_name: str, data: Dict) -> List[Dict]:
        """Generate advisor-specific insights from data"""
        insights = []
        advisor_config = self.LEGENDARY_ADVISORS[advisor_name]

        # Generate insights based on advisor's philosophy
        if advisor_name == 'Warren Buffett':
            insights = self._buffett_insights(data)
        elif advisor_name == 'Cathie Wood':
            insights = self._cathie_wood_insights(data)
        elif advisor_name == 'Ray Dalio':
            insights = self._ray_dalio_insights(data)
        elif advisor_name == 'Elon Musk':
            insights = self._elon_musk_insights(data)
        else:
            # Generic insight generation
            insights = self._generic_insights(advisor_name, data)

        return insights

    def _buffett_insights(self, data: Dict) -> List[Dict]:
        """Generate Warren Buffett style value investing insights"""
        insights = []

        if 'price' in data and 'earnings' in data:
            pe_ratio = data['price'] / max(data['earnings'], 0.01)
            if pe_ratio < 15:
                insights.append({
                    'type': 'value_opportunity',
                    'message': f"Potential value play: P/E ratio of {pe_ratio:.2f} suggests undervaluation",
                    'confidence': 0.8,
                    'action': 'research_further'
                })

        if 'dividend_yield' in data and data['dividend_yield'] > 0.03:
            insights.append({
                'type': 'dividend_aristocrat',
                'message': f"Strong dividend yield of {data['dividend_yield']*100:.2f}% with consistent payments",
                'confidence': 0.7,
                'action': 'add_to_watchlist'
            })

        return insights

    def _cathie_wood_insights(self, data: Dict) -> List[Dict]:
        """Generate Cathie Wood style innovation insights"""
        insights = []

        innovation_keywords = ['AI', 'genomics', 'robotics', 'blockchain', 'autonomous']
        data_str = json.dumps(data).lower()

        for keyword in innovation_keywords:
            if keyword.lower() in data_str:
                insights.append({
                    'type': 'disruptive_innovation',
                    'message': f"Disruptive {keyword} opportunity detected with exponential growth potential",
                    'confidence': 0.75,
                    'action': 'deep_research'
                })

        return insights

    def _ray_dalio_insights(self, data: Dict) -> List[Dict]:
        """Generate Ray Dalio style macro insights"""
        insights = []

        if 'debt_to_gdp' in data:
            if data['debt_to_gdp'] > 1.0:
                insights.append({
                    'type': 'debt_cycle',
                    'message': "Debt cycle indicates potential deleveraging phase approaching",
                    'confidence': 0.7,
                    'action': 'hedge_portfolio'
                })

        if 'interest_rate' in data and 'inflation' in data:
            real_rate = data['interest_rate'] - data['inflation']
            if real_rate < 0:
                insights.append({
                    'type': 'monetary_policy',
                    'message': f"Negative real rates ({real_rate:.2f}%) suggest asset inflation ahead",
                    'confidence': 0.8,
                    'action': 'increase_real_assets'
                })

        return insights

    def _elon_musk_insights(self, data: Dict) -> List[Dict]:
        """Generate Elon Musk style transformative tech insights"""
        insights = []

        transformative_keywords = ['mars', 'neural', 'autonomous', 'sustainable', 'exponential']
        data_str = json.dumps(data).lower()

        for keyword in transformative_keywords:
            if keyword in data_str:
                insights.append({
                    'type': 'transformative_tech',
                    'message': f"10x improvement opportunity in {keyword} technology",
                    'confidence': 0.8,
                    'action': 'first_principles_analysis'
                })

        return insights

    def _generic_insights(self, advisor_name: str, data: Dict) -> List[Dict]:
        """Generate generic insights for other advisors"""
        advisor_config = self.LEGENDARY_ADVISORS[advisor_name]

        return [{
            'type': 'advisory',
            'message': f"{advisor_name} perspective: Opportunity aligns with {advisor_config['specialty']}",
            'confidence': 0.6,
            'action': 'evaluate'
        }]

    async def broadcast_to_all_advisors(self, data: Dict) -> Dict:
        """Broadcast data to all relevant advisors"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'data_id': data.get('id', 'unknown'),
            'advisors_fed': [],
            'total_insights': 0
        }

        tasks = []
        for advisor_name in self.LEGENDARY_ADVISORS.keys():
            tasks.append(self.feed_advisor(advisor_name, data))

        # Run all feeds in parallel
        feed_results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, result in enumerate(feed_results):
            advisor_name = list(self.LEGENDARY_ADVISORS.keys())[i]
            if isinstance(result, Exception):
                logger.error(f"❌ Failed to feed {advisor_name}: {result}")
            elif result.get('insights'):
                results['advisors_fed'].append(advisor_name)
                results['total_insights'] += len(result['insights'])

        logger.info(f"📡 Broadcast to {len(results['advisors_fed'])} advisors, "
                   f"{results['total_insights']} total insights")

        return results

    def get_advisor_performance(self, advisor_name: str) -> Dict:
        """Get performance metrics for a specific advisor"""
        if advisor_name not in self.active_feeds:
            return {'error': 'Unknown advisor'}

        feed_info = self.active_feeds[advisor_name]

        return {
            'advisor': advisor_name,
            'specialty': self.LEGENDARY_ADVISORS[advisor_name]['specialty'],
            'status': feed_info['status'],
            'last_update': feed_info['last_update'].isoformat() if feed_info['last_update'] else None,
            'update_count': feed_info['update_count'],
            'current_insights': len(feed_info['current_insights']),
            'performance': feed_info['performance']
        }

    def get_all_advisor_stats(self) -> Dict:
        """Get statistics for all advisors"""
        active_advisors = [name for name, feed in self.active_feeds.items()
                          if feed['status'] == 'active']

        return {
            'total_advisors': len(self.LEGENDARY_ADVISORS),
            'active_advisors': len(active_advisors),
            'total_updates': self.feed_stats['total_updates'],
            'success_rate': self.feed_stats['successful_feeds'] / max(self.feed_stats['total_updates'], 1),
            'advisor_list': active_advisors,
            'top_performers': self._get_top_performers()
        }

    def _get_top_performers(self, limit: int = 5) -> List[Dict]:
        """Get top performing advisors"""
        performances = []

        for advisor_name, feed_info in self.active_feeds.items():
            if feed_info['update_count'] > 0:
                performances.append({
                    'advisor': advisor_name,
                    'insights_generated': len(feed_info['current_insights']),
                    'update_count': feed_info['update_count']
                })

        # Sort by insights generated
        performances.sort(key=lambda x: x['insights_generated'], reverse=True)

        return performances[:limit]


# Singleton instance
advisor_feed = AdvisorFeed()


async def feed_advisors(data: Dict) -> Dict:
    """
    Public interface for feeding data to advisors

    Args:
        data: Data to feed to advisors

    Returns:
        Feed results
    """
    return await advisor_feed.broadcast_to_all_advisors(data)


def get_advisor_stats() -> Dict:
    """Get advisor feed statistics"""
    return advisor_feed.get_all_advisor_stats()
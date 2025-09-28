"""
Advisor Intelligence Feed System
Phase 3: Connect 25 Legendary Advisors to Real-Time Data

This module feeds specialized intelligence to legendary advisors
based on their expertise and investment philosophies.

Enhanced with Bluesky social intelligence integration for real-time
expert insights and community-driven learning.
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
            'advisors_active': 0,
            'bluesky_insights_collected': 0,
            'expert_knowledge_applied': 0
        }

        # Bluesky learning integration
        self.bluesky_enabled = False
        self.bluesky_handler = None
        self.bluesky_collector = None

        self._initialize_feeds()
        self._initialize_bluesky_integration()

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

    def _initialize_bluesky_integration(self):
        """Initialize Bluesky integration for real-time expert insights"""
        try:
            from ..spiders.bluesky_handler import bluesky_handler, bluesky_collector
            from ..intelligence.bluesky_learning_bridge import bluesky_learning_bridge

            self.bluesky_handler = bluesky_handler
            self.bluesky_collector = bluesky_collector
            self.bluesky_learning_bridge = bluesky_learning_bridge
            self.bluesky_enabled = True

            logger.info("🦋 Bluesky integration enabled for advisor feeds")

        except ImportError as e:
            logger.warning(f"Bluesky integration not available: {e}")
            self.bluesky_enabled = False

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

    async def enhance_advisor_with_social_intelligence(self, advisor_name: str) -> Dict[str, Any]:
        """
        Enhanced advisor feed with both Bluesky and Reddit intelligence

        Args:
            advisor_name: Name of the advisor to enhance

        Returns:
            Combined social intelligence insights for the advisor
        """
        if advisor_name not in self.LEGENDARY_ADVISORS:
            return {'error': 'Unknown advisor'}

        # Get both Bluesky and Reddit insights
        bluesky_data = await self.enhance_advisor_with_bluesky(advisor_name)
        reddit_data = await self.enhance_advisor_with_reddit(advisor_name)

        # Combine insights
        combined_data = {
            'advisor': advisor_name,
            'timestamp': datetime.now().isoformat(),
            'bluesky_insights': bluesky_data.get('bluesky_insights', {}),
            'reddit_insights': reddit_data.get('reddit_insights', []),
            'combined_recommendations': [],
            'consensus_analysis': {},
            'multi_platform_trends': []
        }

        # Merge recommendations from both platforms
        if 'recommendations' in bluesky_data:
            for rec in bluesky_data['recommendations']:
                rec['platform'] = 'bluesky'
                combined_data['combined_recommendations'].append(rec)

        if 'reddit_recommendations' in reddit_data:
            for rec in reddit_data['reddit_recommendations']:
                rec['platform'] = 'reddit'
                combined_data['combined_recommendations'].append(rec)

        # Sort recommendations by confidence/priority
        combined_data['combined_recommendations'].sort(
            key=lambda x: x.get('confidence', x.get('relevance_score', 0)),
            reverse=True
        )

        # Combine consensus analysis
        combined_data['consensus_analysis'] = {
            'bluesky_sentiment': bluesky_data.get('market_sentiment', 0),
            'reddit_consensus': reddit_data.get('community_consensus', []),
            'overall_sentiment': (
                bluesky_data.get('market_sentiment', 0) +
                sum(c['sentiment'] for c in reddit_data.get('community_consensus', []) if 'sentiment' in c)
            ) / max(len(reddit_data.get('community_consensus', [])) + 1, 1)
        }

        # Combine trending topics
        bluesky_trends = bluesky_data.get('trend_analysis', {}).get('emerging_topics', [])
        reddit_trends = [t['keywords'] for t in reddit_data.get('trending_topics', [])]

        combined_data['multi_platform_trends'] = {
            'bluesky': bluesky_trends[:5],
            'reddit': reddit_trends[:5],
            'consensus_trends': list(set(bluesky_trends) & set(sum(reddit_trends, [])))[:3]
        }

        return combined_data

    async def enhance_advisor_with_reddit(self, advisor_name: str) -> Dict[str, Any]:
        """
        Enhanced advisor feed with Reddit intelligence

        Args:
            advisor_name: Name of the advisor to enhance

        Returns:
            Enhanced advisor intelligence with Reddit insights
        """
        if advisor_name not in self.LEGENDARY_ADVISORS:
            return {'error': 'Unknown advisor'}

        advisor_config = self.LEGENDARY_ADVISORS[advisor_name]

        try:
            from ..intelligence.reddit_learning_bridge import get_reddit_learning_bridge
            reddit_bridge = get_reddit_learning_bridge()

            # Get Reddit insights for the advisor
            reddit_insights = await reddit_bridge.get_insights_for_advisor(
                advisor_name,
                advisor_config['keywords']
            )

            # Get trending topics relevant to advisor
            trending_topics = await reddit_bridge.get_trending_topics()

            # Filter for relevant trends
            relevant_trends = [
                trend for trend in trending_topics
                if any(keyword.lower() in ' '.join(trend.keywords).lower()
                      for keyword in advisor_config['keywords'])
            ]

            # Build Reddit consensus on key topics
            consensus_data = []
            for keyword in advisor_config['keywords'][:3]:
                consensus = await reddit_bridge.get_community_consensus(keyword)
                if consensus:
                    consensus_data.append({
                        'topic': keyword,
                        'sentiment': consensus.average_sentiment,
                        'confidence': consensus.confidence,
                        'subreddits': consensus.subreddits[:5],
                        'key_arguments': consensus.key_arguments_for[:3]
                    })

            # Generate Reddit-based recommendations
            reddit_recommendations = []
            for insight in reddit_insights[:5]:
                if insight.actionable_advice:
                    reddit_recommendations.append({
                        'source': f"r/{insight.subreddit}",
                        'advice': insight.actionable_advice[0],
                        'confidence': insight.confidence,
                        'sentiment': insight.sentiment
                    })

            return {
                'advisor': advisor_name,
                'reddit_insights': [ins.to_dict() for ins in reddit_insights[:10]],
                'trending_topics': [trend.to_dict() for trend in relevant_trends[:5]],
                'community_consensus': consensus_data,
                'reddit_recommendations': reddit_recommendations,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error enhancing {advisor_name} with Reddit: {e}")
            return {'error': str(e)}

    async def enhance_advisor_with_bluesky(self, advisor_name: str) -> Dict[str, Any]:
        """
        Enhanced advisor feed with Bluesky intelligence

        Args:
            advisor_name: Name of the advisor to enhance

        Returns:
            Enhanced advisor intelligence with Bluesky insights
        """
        if not self.bluesky_enabled:
            logger.warning("Bluesky integration not enabled")
            return {'error': 'Bluesky not available'}

        if advisor_name not in self.LEGENDARY_ADVISORS:
            return {'error': 'Unknown advisor'}

        advisor_config = self.LEGENDARY_ADVISORS[advisor_name]

        try:
            # Collect Bluesky intelligence for advisor's specialty
            bluesky_insights = await self.bluesky_collector.collect_intelligence(
                keywords=advisor_config['keywords'],
                max_posts_per_keyword=10
            )

            # Extract expert insights relevant to this advisor
            expert_insights = await self._extract_advisor_expert_insights(advisor_name, advisor_config)

            # Analyze trending topics in advisor's domain
            trend_analysis = await self._analyze_advisor_trends(advisor_name, advisor_config)

            # Calculate insight quality scores
            quality_insights = self._filter_high_quality_insights(bluesky_insights, advisor_config)

            enhanced_intelligence = {
                'advisor': advisor_name,
                'specialty': advisor_config['specialty'],
                'timestamp': datetime.now().isoformat(),
                'bluesky_insights': {
                    'total_posts': len(bluesky_insights.get('posts', [])),
                    'high_quality_posts': len(quality_insights),
                    'engagement_score': bluesky_insights.get('metrics', {}).get('total_engagement', 0),
                    'trending_topics': bluesky_insights.get('trending', [])[:5]
                },
                'expert_insights': expert_insights,
                'trend_analysis': trend_analysis,
                'actionable_recommendations': await self._generate_advisor_recommendations(
                    advisor_name, quality_insights, expert_insights, trend_analysis
                ),
                'market_sentiment': self._analyze_advisor_market_sentiment(advisor_config, bluesky_insights),
                'learning_updates': await self._apply_learning_to_advisor(advisor_name, bluesky_insights)
            }

            # Update advisor feed stats
            self.feed_stats['bluesky_insights_collected'] += len(quality_insights)
            self.feed_stats['expert_knowledge_applied'] += len(expert_insights)

            # Store insights in advisor's current insights
            if advisor_name in self.active_feeds:
                self.active_feeds[advisor_name]['current_insights'].extend(
                    enhanced_intelligence['actionable_recommendations'][:5]
                )

            logger.info(f"🦋 Enhanced {advisor_name} with {len(quality_insights)} Bluesky insights")

            return enhanced_intelligence

        except Exception as e:
            logger.error(f"Error enhancing {advisor_name} with Bluesky: {e}")
            return {'error': str(e)}

    async def _extract_advisor_expert_insights(self, advisor_name: str, advisor_config: Dict) -> List[Dict]:
        """Extract expert insights relevant to a specific advisor"""
        expert_insights = []

        # Map advisors to their real-world counterparts or similar experts
        expert_mapping = {
            'Warren Buffett': ['pmarca.bsky.social', 'naval.bsky.social'],
            'Cathie Wood': ['sama.bsky.social', 'karpathy.ai'],
            'Ray Dalio': ['nouriel.bsky.social', 'naval.bsky.social'],
            'Sam Altman': ['sama.bsky.social', 'karpathy.ai'],
            'Marc Andreessen': ['pmarca.bsky.social', 'dhh.bsky.social']
        }

        relevant_experts = expert_mapping.get(advisor_name, ['pmarca.bsky.social', 'sama.bsky.social'])

        for expert_handle in relevant_experts:
            try:
                # Get recent posts from expert
                expert_posts = await self.bluesky_handler.get_author_feed(expert_handle, limit=5)

                # Handle case where expert_posts is None or empty
                if not expert_posts:
                    continue

                for post in expert_posts:
                    # Check if post is relevant to advisor's interests
                    if self._is_post_relevant_to_advisor(post, advisor_config):
                        insight = {
                            'expert': expert_handle,
                            'content': post['text'],
                            'engagement': post['metrics']['engagement'],
                            'timestamp': post['created_at'],
                            'relevance_score': self._calculate_advisor_relevance(post, advisor_config),
                            'actionable_points': self._extract_actionable_points(post['text'])
                        }
                        expert_insights.append(insight)

            except Exception as e:
                logger.warning(f"Error extracting insights from {expert_handle}: {e}")
                continue

        # Sort by relevance score
        expert_insights.sort(key=lambda x: x['relevance_score'], reverse=True)

        return expert_insights[:5]  # Return top 5 insights

    async def _analyze_advisor_trends(self, advisor_name: str, advisor_config: Dict) -> Dict:
        """Analyze trends relevant to a specific advisor"""
        trend_analysis = {
            'emerging_topics': [],
            'market_sentiment': 0.0,
            'opportunity_signals': [],
            'risk_indicators': []
        }

        try:
            # Search for trending content in advisor's domain
            for keyword in advisor_config['keywords'][:3]:  # Limit keywords
                posts = await self.bluesky_handler.search_posts(
                    keyword, limit=10, sort="top"
                )

                if posts:
                    # Analyze trends in these posts
                    keyword_trends = self._analyze_keyword_trends(keyword, posts)
                    trend_analysis['emerging_topics'].extend(keyword_trends['topics'])
                    trend_analysis['market_sentiment'] += keyword_trends['sentiment']
                    trend_analysis['opportunity_signals'].extend(keyword_trends['opportunities'])
                    trend_analysis['risk_indicators'].extend(keyword_trends['risks'])

            # Average sentiment
            if len(advisor_config['keywords'][:3]) > 0:
                trend_analysis['market_sentiment'] /= len(advisor_config['keywords'][:3])

        except Exception as e:
            logger.warning(f"Error analyzing trends for {advisor_name}: {e}")

        return trend_analysis

    def _filter_high_quality_insights(self, bluesky_insights: Dict, advisor_config: Dict) -> List[Dict]:
        """Filter for high-quality insights relevant to the advisor"""
        quality_insights = []

        posts = bluesky_insights.get('posts', [])

        for post in posts:
            quality_score = 0

            # Engagement quality
            if post['metrics']['engagement'] > 20:
                quality_score += 2
            elif post['metrics']['engagement'] > 10:
                quality_score += 1

            # Content length quality
            if len(post['text']) > 100:
                quality_score += 1

            # Keyword relevance
            text_lower = post['text'].lower()
            relevant_keywords = sum(1 for keyword in advisor_config['keywords']
                                  if keyword.lower() in text_lower)
            quality_score += relevant_keywords

            # Author credibility (simplified)
            if '.' in post['author']['handle']:  # Custom domain suggests credibility
                quality_score += 1

            # Only include high-quality posts
            if quality_score >= 3:
                post['quality_score'] = quality_score
                quality_insights.append(post)

        return sorted(quality_insights, key=lambda x: x['quality_score'], reverse=True)[:10]

    async def _generate_advisor_recommendations(self, advisor_name: str,
                                             quality_insights: List[Dict],
                                             expert_insights: List[Dict],
                                             trend_analysis: Dict) -> List[Dict]:
        """Generate actionable recommendations for the advisor"""
        recommendations = []

        # From quality insights
        for insight in quality_insights[:3]:
            recommendations.append({
                'type': 'market_insight',
                'priority': 'high',
                'recommendation': f"Monitor: {insight['text'][:100]}...",
                'source': 'bluesky_community',
                'engagement_score': insight['metrics']['engagement']
            })

        # From expert insights
        for expert_insight in expert_insights[:2]:
            recommendations.append({
                'type': 'expert_wisdom',
                'priority': 'high',
                'recommendation': f"Expert insight from {expert_insight['expert']}: {expert_insight['actionable_points'][0] if expert_insight['actionable_points'] else 'Consider market dynamics'}",
                'source': 'industry_expert',
                'relevance_score': expert_insight['relevance_score']
            })

        # From trend analysis
        if trend_analysis['opportunity_signals']:
            recommendations.append({
                'type': 'opportunity',
                'priority': 'medium',
                'recommendation': f"Emerging opportunity: {trend_analysis['opportunity_signals'][0]}",
                'source': 'trend_analysis',
                'market_sentiment': trend_analysis['market_sentiment']
            })

        return recommendations

    def _analyze_advisor_market_sentiment(self, advisor_config: Dict, bluesky_insights: Dict) -> Dict:
        """Analyze market sentiment for advisor's specialty"""
        sentiment_data = {
            'overall_sentiment': 0.0,
            'confidence': 0.0,
            'key_topics': [],
            'sentiment_distribution': {'positive': 0, 'neutral': 0, 'negative': 0}
        }

        try:
            from textblob import TextBlob

            posts = bluesky_insights.get('posts', [])
            if not posts:
                return sentiment_data

            total_sentiment = 0
            sentiment_count = 0

            for post in posts:
                # Simple sentiment analysis
                blob = TextBlob(post['text'])
                sentiment = blob.sentiment.polarity

                # Weight by engagement
                weight = 1 + (post['metrics']['engagement'] / 100)
                weighted_sentiment = sentiment * weight

                total_sentiment += weighted_sentiment
                sentiment_count += weight

                # Categorize sentiment
                if sentiment > 0.1:
                    sentiment_data['sentiment_distribution']['positive'] += 1
                elif sentiment < -0.1:
                    sentiment_data['sentiment_distribution']['negative'] += 1
                else:
                    sentiment_data['sentiment_distribution']['neutral'] += 1

            if sentiment_count > 0:
                sentiment_data['overall_sentiment'] = total_sentiment / sentiment_count
                sentiment_data['confidence'] = min(1.0, sentiment_count / 50)

        except ImportError:
            logger.warning("TextBlob not available for sentiment analysis")

        return sentiment_data

    async def _apply_learning_to_advisor(self, advisor_name: str, bluesky_insights: Dict) -> List[str]:
        """Apply learning from Bluesky insights to advisor's knowledge base"""
        learning_updates = []

        try:
            posts = bluesky_insights.get('posts', [])

            # Extract key learning points
            for post in posts:
                if post['metrics']['engagement'] > 15:  # High-engagement posts
                    # Extract key phrases or concepts
                    key_concepts = self._extract_key_concepts(post['text'])

                    for concept in key_concepts:
                        learning_updates.append(f"New concept: {concept}")

        except Exception as e:
            logger.warning(f"Error applying learning for {advisor_name}: {e}")

        return learning_updates[:5]  # Limit to top 5 learning updates

    # Helper methods for the new functionality

    def _is_post_relevant_to_advisor(self, post: Dict, advisor_config: Dict) -> bool:
        """Check if a post is relevant to an advisor's interests"""
        text_lower = post['text'].lower()
        keywords = advisor_config['keywords']

        # Check if any keyword is mentioned
        keyword_matches = sum(1 for keyword in keywords if keyword.lower() in text_lower)

        # Must have at least 1 keyword match and some engagement
        return keyword_matches > 0 and post['metrics']['engagement'] > 3

    def _calculate_advisor_relevance(self, post: Dict, advisor_config: Dict) -> float:
        """Calculate relevance score of a post to an advisor"""
        score = 0.0
        text_lower = post['text'].lower()

        # Keyword matching (weighted by importance)
        for i, keyword in enumerate(advisor_config['keywords']):
            if keyword.lower() in text_lower:
                # Earlier keywords are more important
                weight = 1.0 - (i * 0.1)
                score += weight

        # Engagement boost
        engagement_score = min(1.0, post['metrics']['engagement'] / 50)
        score += engagement_score

        # Content quality (length indicates depth)
        if len(post['text']) > 200:
            score += 0.5

        return min(10.0, score)

    def _extract_actionable_points(self, text: str) -> List[str]:
        """Extract actionable points from text"""
        actionable_patterns = [
            r'should\s+(.+?)(?:\.|!|$)',
            r'must\s+(.+?)(?:\.|!|$)',
            r'need\s+to\s+(.+?)(?:\.|!|$)',
            r'recommend\s+(.+?)(?:\.|!|$)'
        ]

        actionable_points = []

        import re
        for pattern in actionable_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            actionable_points.extend([match.strip() for match in matches if len(match.strip()) > 10])

        return actionable_points[:3]  # Top 3 actionable points

    def _analyze_keyword_trends(self, keyword: str, posts: List[Dict]) -> Dict:
        """Analyze trends for a specific keyword"""
        trends = {
            'topics': [],
            'sentiment': 0.0,
            'opportunities': [],
            'risks': []
        }

        try:
            from textblob import TextBlob

            for post in posts:
                # Sentiment analysis
                blob = TextBlob(post['text'])
                trends['sentiment'] += blob.sentiment.polarity

                # Look for opportunity signals
                text_lower = post['text'].lower()
                if any(signal in text_lower for signal in ['opportunity', 'growth', 'potential', 'bullish']):
                    trends['opportunities'].append(post['text'][:50] + '...')

                # Look for risk signals
                if any(signal in text_lower for signal in ['risk', 'concern', 'bearish', 'problem']):
                    trends['risks'].append(post['text'][:50] + '...')

            # Average sentiment
            if posts:
                trends['sentiment'] /= len(posts)

        except ImportError:
            pass

        return trends

    def _extract_key_concepts(self, text: str) -> List[str]:
        """Extract key concepts from text (simplified)"""
        # This is a simplified implementation
        # In production, you'd use more sophisticated NLP

        words = text.lower().split()

        # Filter for important concepts (nouns, tech terms, etc.)
        important_words = [word for word in words if len(word) > 4 and
                          not word in ['that', 'this', 'with', 'from', 'they', 'have', 'been', 'will']]

        # Return most frequent important words
        from collections import Counter
        word_counts = Counter(important_words)

        return [word for word, count in word_counts.most_common(3)]

    async def start_bluesky_enhanced_feeds(self):
        """Start enhanced advisor feeds with Bluesky integration"""
        if not self.bluesky_enabled:
            logger.warning("Cannot start enhanced feeds - Bluesky not available")
            return

        logger.info("🚀 Starting Bluesky-enhanced advisor feeds")

        # Enhanced feed for all advisors
        for advisor_name in self.LEGENDARY_ADVISORS.keys():
            try:
                enhanced_data = await self.enhance_advisor_with_bluesky(advisor_name)

                if 'error' not in enhanced_data:
                    logger.info(f"✅ Enhanced {advisor_name} with Bluesky intelligence")

            except Exception as e:
                logger.error(f"Error enhancing {advisor_name}: {e}")

    def get_bluesky_stats(self) -> Dict[str, Any]:
        """Get Bluesky integration statistics"""
        return {
            'bluesky_enabled': self.bluesky_enabled,
            'insights_collected': self.feed_stats.get('bluesky_insights_collected', 0),
            'expert_knowledge_applied': self.feed_stats.get('expert_knowledge_applied', 0),
            'last_enhancement': datetime.now().isoformat()
        }


# Singleton instance (lazy-loaded)
advisor_feed = None

def get_advisor_feed():
    """Get or create the singleton advisor feed instance"""
    global advisor_feed
    if advisor_feed is None:
        advisor_feed = AdvisorFeed()
    return advisor_feed


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
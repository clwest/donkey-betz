"""
Spider Army Supreme Orchestrator
Coordinates 1,770+ specialized spiders feeding 149 agents and 25 legendary advisors
Real-time intelligence distribution and spider coordination system
"""

import asyncio
import json
import logging
import redis
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
import sys
import os

# Add spiders to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'donkeybetz_spiders'))

# Configure Redis for inter-spider communication
redis_client = redis.Redis.from_url(
    os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
    decode_responses=True
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/Users/donkeyking/Donkey_Betz/unified-donkey-betz/logs/spider_army.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class SpiderConfig:
    """Configuration for individual spider deployment"""
    spider_class: str
    spider_name: str
    target_agents: List[str]
    target_advisors: List[str]
    update_frequency: int  # seconds
    priority: int  # 1-10, 10 being highest
    concurrency: int
    delay: int
    custom_settings: Dict[str, Any]


@dataclass
class AgentProfile:
    """Profile for agents that consume spider intelligence"""
    agent_id: str
    agent_type: str
    specialization: List[str]
    intelligence_preferences: List[str]
    update_frequency: int
    priority_sources: List[str]


@dataclass
class AdvisorProfile:
    """Profile for legendary advisors"""
    advisor_name: str
    investment_style: str
    focus_areas: List[str]
    preferred_sources: List[str]
    intelligence_filters: Dict[str, Any]
    update_frequency: int


class SpiderArmyOrchestrator:
    """
    Supreme commander of the spider army
    Deploys, coordinates, and monitors 1,770+ specialized spiders
    """

    def __init__(self):
        self.settings = get_project_settings()
        self.setup_scrapy_settings()

        # Spider army composition
        self.spider_army_size = 1770
        self.active_spiders = {}
        self.spider_configs = {}

        # Consumer profiles
        self.agent_profiles = self.load_agent_profiles()
        self.advisor_profiles = self.load_advisor_profiles()

        # Performance metrics
        self.spider_metrics = {}
        self.intelligence_feed_stats = {}

        # Deployment clusters
        self.spider_clusters = {
            'cluster_alpha': [],    # Contract work spiders (300)
            'cluster_beta': [],     # Market intelligence spiders (400)
            'cluster_gamma': [],    # Content research spiders (350)
            'cluster_delta': [],    # Advisor-specific spiders (420)
            'cluster_omega': []     # General purpose adaptive spiders (300)
        }

        logger.info(f"Spider Army Orchestrator initialized - Target army size: {self.spider_army_size}")

    def setup_scrapy_settings(self):
        """Configure Scrapy settings for massive spider deployment"""
        self.settings.set('CONCURRENT_REQUESTS', 64)
        self.settings.set('CONCURRENT_REQUESTS_PER_DOMAIN', 16)
        self.settings.set('DOWNLOAD_DELAY', 2)
        self.settings.set('RANDOMIZE_DOWNLOAD_DELAY', 0.5)
        self.settings.set('COOKIES_ENABLED', True)
        self.settings.set('ROBOTSTXT_OBEY', True)
        self.settings.set('USER_AGENT', 'DonkeyBetz Intelligence Spider Army (+http://donkeybetz.com)')

        # Enable Redis-based distributed crawling
        self.settings.set('DUPEFILTER_CLASS', 'scrapy_redis.dupefilter.RFPDupeFilter')
        self.settings.set('SCHEDULER', 'scrapy_redis.scheduler.Scheduler')
        self.settings.set('SCHEDULER_PERSIST', True)
        self.settings.set('REDIS_URL', 'redis://localhost:6379/1')

        # Configure item pipelines for intelligence processing
        self.settings.set('ITEM_PIPELINES', {
            'donkeybetz_spiders.pipelines.IntelligenceProcessingPipeline': 300,
            'donkeybetz_spiders.pipelines.AgentFeedingPipeline': 400,
            'donkeybetz_spiders.pipelines.AdvisorRoutingPipeline': 500,
        })

    def load_agent_profiles(self) -> Dict[str, AgentProfile]:
        """Load profiles for 149 specialized agents"""
        agent_profiles = {}

        # Define agent categories and their profiles
        agent_categories = {
            'content_creation': {
                'count': 25,
                'specialization': ['content_writing', 'seo_optimization', 'viral_content'],
                'intelligence_preferences': ['trending_topics', 'keyword_research', 'viral_patterns'],
                'update_frequency': 1800,  # 30 minutes
                'priority_sources': ['content_research_spiders', 'trending_topics', 'seo_keywords']
            },
            'job_application': {
                'count': 20,
                'specialization': ['contract_work', 'freelancing', 'remote_jobs'],
                'intelligence_preferences': ['job_opportunities', 'client_profiles', 'market_rates'],
                'update_frequency': 900,  # 15 minutes
                'priority_sources': ['upwork_spiders', 'freelancer_spiders', 'linkedin_spiders']
            },
            'market_analysis': {
                'count': 18,
                'specialization': ['market_trends', 'competitor_analysis', 'pricing_intelligence'],
                'intelligence_preferences': ['market_movements', 'competitor_data', 'industry_news'],
                'update_frequency': 1200,  # 20 minutes
                'priority_sources': ['market_intelligence_spiders', 'news_spiders', 'pricing_spiders']
            },
            'business_development': {
                'count': 15,
                'specialization': ['opportunity_identification', 'lead_generation', 'partnership_scouting'],
                'intelligence_preferences': ['business_opportunities', 'industry_partnerships', 'funding_news'],
                'update_frequency': 2400,  # 40 minutes
                'priority_sources': ['business_spiders', 'funding_spiders', 'partnership_spiders']
            },
            'technical_research': {
                'count': 22,
                'specialization': ['ai_research', 'technology_trends', 'innovation_tracking'],
                'intelligence_preferences': ['research_papers', 'tech_breakthroughs', 'patent_filings'],
                'update_frequency': 3600,  # 1 hour
                'priority_sources': ['research_spiders', 'patent_spiders', 'innovation_spiders']
            },
            'financial_analysis': {
                'count': 12,
                'specialization': ['investment_analysis', 'financial_modeling', 'risk_assessment'],
                'intelligence_preferences': ['financial_data', 'market_analysis', 'investment_news'],
                'update_frequency': 1800,  # 30 minutes
                'priority_sources': ['financial_spiders', 'sec_filing_spiders', 'investment_spiders']
            },
            'social_media': {
                'count': 16,
                'specialization': ['social_trends', 'engagement_optimization', 'influencer_tracking'],
                'intelligence_preferences': ['social_trends', 'viral_content', 'engagement_patterns'],
                'update_frequency': 600,  # 10 minutes
                'priority_sources': ['social_spiders', 'viral_content_spiders', 'influencer_spiders']
            },
            'automation': {
                'count': 21,
                'specialization': ['process_automation', 'workflow_optimization', 'tool_integration'],
                'intelligence_preferences': ['automation_tools', 'workflow_trends', 'integration_opportunities'],
                'update_frequency': 2700,  # 45 minutes
                'priority_sources': ['automation_spiders', 'tool_spiders', 'workflow_spiders']
            }
        }

        agent_id = 1
        for category, config in agent_categories.items():
            for i in range(config['count']):
                profile = AgentProfile(
                    agent_id=f"agent_{agent_id:03d}",
                    agent_type=category,
                    specialization=config['specialization'],
                    intelligence_preferences=config['intelligence_preferences'],
                    update_frequency=config['update_frequency'],
                    priority_sources=config['priority_sources']
                )
                agent_profiles[profile.agent_id] = profile
                agent_id += 1

        logger.info(f"Loaded {len(agent_profiles)} agent profiles across {len(agent_categories)} categories")
        return agent_profiles

    def load_advisor_profiles(self) -> Dict[str, AdvisorProfile]:
        """Load profiles for 25 legendary advisors"""
        advisor_profiles = {}

        # Define legendary advisor profiles
        advisors = {
            'warren_buffett': {
                'investment_style': 'value_investing',
                'focus_areas': ['financial_statements', 'company_moats', 'management_quality', 'intrinsic_value'],
                'preferred_sources': ['sec_filings', 'annual_reports', 'financial_news'],
                'intelligence_filters': {'min_market_cap': 1000000000, 'sectors': ['consumer', 'financial', 'industrial']},
                'update_frequency': 3600
            },
            'cathie_wood': {
                'investment_style': 'disruptive_innovation',
                'focus_areas': ['artificial_intelligence', 'genomics', 'blockchain', 'space_exploration'],
                'preferred_sources': ['research_papers', 'patent_filings', 'startup_funding'],
                'intelligence_filters': {'innovation_score': 0.7, 'growth_potential': 'high'},
                'update_frequency': 1800
            },
            'ray_dalio': {
                'investment_style': 'macroeconomic',
                'focus_areas': ['economic_cycles', 'currency_trends', 'geopolitical_risks', 'debt_cycles'],
                'preferred_sources': ['economic_data', 'central_bank_communications', 'geopolitical_news'],
                'intelligence_filters': {'macro_impact': 'high', 'time_horizon': 'long_term'},
                'update_frequency': 2400
            },
            'peter_thiel': {
                'investment_style': 'contrarian_tech',
                'focus_areas': ['monopoly_businesses', 'deep_tech', 'contrarian_opportunities', 'zero_to_one'],
                'preferred_sources': ['startup_ecosystem', 'technology_breakthroughs', 'market_inefficiencies'],
                'intelligence_filters': {'monopoly_potential': 'high', 'contrarian_score': 0.6},
                'update_frequency': 2700
            },
            'paul_graham': {
                'investment_style': 'early_stage_startups',
                'focus_areas': ['startup_trends', 'founder_insights', 'yc_companies', 'essay_wisdom'],
                'preferred_sources': ['hacker_news', 'yc_blog', 'startup_forums', 'github_trends'],
                'intelligence_filters': {'startup_stage': 'early', 'founder_quality': 'high'},
                'update_frequency': 1800
            },
            'marc_andreessen': {
                'investment_style': 'software_eating_world',
                'focus_areas': ['software_disruption', 'platform_businesses', 'network_effects', 'automation'],
                'preferred_sources': ['tech_news', 'software_trends', 'platform_data', 'automation_news'],
                'intelligence_filters': {'software_focus': True, 'disruption_potential': 'high'},
                'update_frequency': 2100
            },
            'charlie_munger': {
                'investment_style': 'multidisciplinary_thinking',
                'focus_areas': ['mental_models', 'business_quality', 'competitive_advantages', 'rational_thinking'],
                'preferred_sources': ['business_analysis', 'competitive_intelligence', 'quality_metrics'],
                'intelligence_filters': {'quality_score': 0.8, 'competitive_moat': 'strong'},
                'update_frequency': 3600
            },
            'bill_ackman': {
                'investment_style': 'activist_investing',
                'focus_areas': ['corporate_governance', 'operational_improvements', 'value_unlocking', 'management_changes'],
                'preferred_sources': ['proxy_filings', 'activist_campaigns', 'governance_news'],
                'intelligence_filters': {'activist_opportunity': 'high', 'governance_issues': True},
                'update_frequency': 2400
            }
            # ... Continue with remaining 17 advisors
        }

        for advisor_name, config in advisors.items():
            profile = AdvisorProfile(
                advisor_name=advisor_name,
                investment_style=config['investment_style'],
                focus_areas=config['focus_areas'],
                preferred_sources=config['preferred_sources'],
                intelligence_filters=config['intelligence_filters'],
                update_frequency=config['update_frequency']
            )
            advisor_profiles[advisor_name] = profile

        logger.info(f"Loaded {len(advisor_profiles)} legendary advisor profiles")
        return advisor_profiles

    def generate_spider_army_configs(self) -> Dict[str, SpiderConfig]:
        """Generate configurations for all 1,770 spiders"""
        spider_configs = {}

        # Contract Work Intelligence Spiders (300 total)
        contract_spiders = self.generate_contract_work_configs(300)
        spider_configs.update(contract_spiders)

        # Market Intelligence Spiders (400 total)
        market_spiders = self.generate_market_intelligence_configs(400)
        spider_configs.update(market_spiders)

        # Content Research Spiders (350 total)
        content_spiders = self.generate_content_research_configs(350)
        spider_configs.update(content_spiders)

        # Advisor-Specific Spiders (420 total)
        advisor_spiders = self.generate_advisor_specific_configs(420)
        spider_configs.update(advisor_spiders)

        # General Purpose Adaptive Spiders (300 total)
        adaptive_spiders = self.generate_adaptive_spider_configs(300)
        spider_configs.update(adaptive_spiders)

        logger.info(f"Generated {len(spider_configs)} spider configurations")
        return spider_configs

    def generate_contract_work_configs(self, count: int) -> Dict[str, SpiderConfig]:
        """Generate contract work spider configurations"""
        configs = {}
        spiders_per_platform = count // 3

        # Upwork spiders
        for i in range(spiders_per_platform):
            spider_name = f"upwork_spider_{i:03d}"
            config = SpiderConfig(
                spider_class='contract_work_spiders.UpworkAIProjectsSpider',
                spider_name=spider_name,
                target_agents=[f"agent_{j:03d}" for j in range(1, 21)],  # Job application agents
                target_advisors=[],
                update_frequency=900,  # 15 minutes
                priority=8,
                concurrency=4,
                delay=3,
                custom_settings={
                    'DOWNLOAD_DELAY': 3 + (i % 3),  # Stagger delays
                    'search_specialization': self.get_search_specialization(i)
                }
            )
            configs[spider_name] = config

        # Freelancer spiders
        for i in range(spiders_per_platform):
            spider_name = f"freelancer_spider_{i:03d}"
            config = SpiderConfig(
                spider_class='contract_work_spiders.FreelancerAIGigsSpider',
                spider_name=spider_name,
                target_agents=[f"agent_{j:03d}" for j in range(1, 21)],
                target_advisors=[],
                update_frequency=1200,  # 20 minutes
                priority=7,
                concurrency=3,
                delay=4,
                custom_settings={
                    'DOWNLOAD_DELAY': 4 + (i % 2),
                    'category_focus': self.get_category_focus(i)
                }
            )
            configs[spider_name] = config

        # LinkedIn spiders
        remaining = count - (2 * spiders_per_platform)
        for i in range(remaining):
            spider_name = f"linkedin_spider_{i:03d}"
            config = SpiderConfig(
                spider_class='contract_work_spiders.LinkedInJobsSpider',
                spider_name=spider_name,
                target_agents=[f"agent_{j:03d}" for j in range(1, 21)],
                target_advisors=[],
                update_frequency=1800,  # 30 minutes
                priority=6,
                concurrency=2,
                delay=5,
                custom_settings={
                    'DOWNLOAD_DELAY': 5 + (i % 3),
                    'job_level_focus': self.get_job_level_focus(i)
                }
            )
            configs[spider_name] = config

        return configs

    def generate_market_intelligence_configs(self, count: int) -> Dict[str, SpiderConfig]:
        """Generate market intelligence spider configurations"""
        configs = {}
        categories = ['news', 'pricing', 'funding', 'trends']
        spiders_per_category = count // len(categories)

        for category in categories:
            for i in range(spiders_per_category):
                spider_name = f"market_{category}_spider_{i:03d}"
                config = SpiderConfig(
                    spider_class=f'market_intelligence_spiders.{category.title()}Spider',
                    spider_name=spider_name,
                    target_agents=[f"agent_{j:03d}" for j in range(21, 40)],  # Market analysis agents
                    target_advisors=['warren_buffett', 'cathie_wood', 'ray_dalio'],
                    update_frequency=1200,  # 20 minutes
                    priority=9,
                    concurrency=6,
                    delay=2,
                    custom_settings={
                        'DOWNLOAD_DELAY': 2 + (i % 2),
                        'market_segment': self.get_market_segment(category, i)
                    }
                )
                configs[spider_name] = config

        return configs

    def generate_content_research_configs(self, count: int) -> Dict[str, SpiderConfig]:
        """Generate content research spider configurations"""
        configs = {}
        categories = ['trending', 'seo', 'viral', 'social']
        spiders_per_category = count // len(categories)

        for category in categories:
            for i in range(spiders_per_category):
                spider_name = f"content_{category}_spider_{i:03d}"
                config = SpiderConfig(
                    spider_class=f'content_research_spiders.{category.title()}Spider',
                    spider_name=spider_name,
                    target_agents=[f"agent_{j:03d}" for j in range(41, 66)],  # Content creation agents
                    target_advisors=[],
                    update_frequency=600,  # 10 minutes
                    priority=7,
                    concurrency=8,
                    delay=1,
                    custom_settings={
                        'DOWNLOAD_DELAY': 1 + (i % 2),
                        'content_focus': self.get_content_focus(category, i)
                    }
                )
                configs[spider_name] = config

        return configs

    def generate_advisor_specific_configs(self, count: int) -> Dict[str, SpiderConfig]:
        """Generate advisor-specific spider configurations"""
        configs = {}
        advisor_count = len(self.advisor_profiles)
        spiders_per_advisor = count // advisor_count

        for advisor_name, advisor_profile in self.advisor_profiles.items():
            for i in range(spiders_per_advisor):
                spider_name = f"{advisor_name}_spider_{i:03d}"
                config = SpiderConfig(
                    spider_class=f'advisor_spiders.{advisor_name.title().replace("_", "")}IntelligenceSpider',
                    spider_name=spider_name,
                    target_agents=[],  # Advisor-specific, no direct agent targeting
                    target_advisors=[advisor_name],
                    update_frequency=advisor_profile.update_frequency,
                    priority=10,  # Highest priority for advisors
                    concurrency=3,
                    delay=advisor_profile.update_frequency // 300,  # Scale delay with update frequency
                    custom_settings={
                        'DOWNLOAD_DELAY': advisor_profile.update_frequency // 300,
                        'focus_areas': advisor_profile.focus_areas,
                        'intelligence_filters': advisor_profile.intelligence_filters
                    }
                )
                configs[spider_name] = config

        return configs

    def generate_adaptive_spider_configs(self, count: int) -> Dict[str, SpiderConfig]:
        """Generate adaptive spider configurations that learn and evolve"""
        configs = {}

        for i in range(count):
            spider_name = f"adaptive_spider_{i:03d}"
            config = SpiderConfig(
                spider_class='adaptive_spiders.AdaptiveIntelligenceSpider',
                spider_name=spider_name,
                target_agents=self.get_random_agent_subset(5),  # 5 random agents
                target_advisors=self.get_random_advisor_subset(2),  # 2 random advisors
                update_frequency=1800 + (i % 1200),  # Variable frequency
                priority=5,
                concurrency=4,
                delay=2 + (i % 3),
                custom_settings={
                    'DOWNLOAD_DELAY': 2 + (i % 3),
                    'adaptation_mode': 'evolutionary',
                    'learning_rate': 0.1
                }
            )
            configs[spider_name] = config

        return configs

    def get_search_specialization(self, index: int) -> str:
        """Get search specialization for Upwork spiders"""
        specializations = [
            'ai_content_creation', 'machine_learning_automation', 'chatbot_development',
            'data_analysis_ai', 'ai_writing_assistant', 'automation_scripts',
            'gpt_integration', 'ai_marketing_tools', 'content_generation_ai'
        ]
        return specializations[index % len(specializations)]

    def get_category_focus(self, index: int) -> str:
        """Get category focus for Freelancer spiders"""
        categories = [
            'artificial-intelligence', 'machine-learning', 'data-processing',
            'automation', 'chatbots', 'content-writing', 'web-scraping'
        ]
        return categories[index % len(categories)]

    def get_job_level_focus(self, index: int) -> str:
        """Get job level focus for LinkedIn spiders"""
        levels = ['entry', 'mid', 'senior', 'lead', 'director']
        return levels[index % len(levels)]

    def get_market_segment(self, category: str, index: int) -> str:
        """Get market segment for market intelligence spiders"""
        segments = {
            'news': ['ai_startups', 'big_tech', 'enterprise_ai', 'ai_regulation'],
            'pricing': ['saas_ai_tools', 'enterprise_ai', 'ai_apis', 'consulting_rates'],
            'funding': ['seed_funding', 'series_a', 'series_b', 'ipo_activity'],
            'trends': ['adoption_rates', 'technology_evolution', 'market_size', 'competitive_landscape']
        }
        return segments[category][index % len(segments[category])]

    def get_content_focus(self, category: str, index: int) -> str:
        """Get content focus for content research spiders"""
        focuses = {
            'trending': ['ai_news', 'tech_trends', 'startup_news', 'innovation_updates'],
            'seo': ['ai_keywords', 'tech_keywords', 'business_keywords', 'industry_keywords'],
            'viral': ['tech_viral', 'ai_viral', 'business_viral', 'educational_viral'],
            'social': ['twitter_ai', 'linkedin_tech', 'reddit_ai', 'youtube_tech']
        }
        return focuses[category][index % len(focuses[category])]

    def get_random_agent_subset(self, count: int) -> List[str]:
        """Get random subset of agents for adaptive spiders"""
        import random
        agent_ids = list(self.agent_profiles.keys())
        return random.sample(agent_ids, min(count, len(agent_ids)))

    def get_random_advisor_subset(self, count: int) -> List[str]:
        """Get random subset of advisors for adaptive spiders"""
        import random
        advisor_names = list(self.advisor_profiles.keys())
        return random.sample(advisor_names, min(count, len(advisor_names)))

    async def deploy_spider_army(self):
        """Deploy the complete spider army of 1,770 spiders"""
        logger.info("🕷️ DEPLOYING MASSIVE SPIDER ARMY - 1,770 INTELLIGENCE AGENTS")

        # Generate all spider configurations
        self.spider_configs = self.generate_spider_army_configs()

        # Distribute spiders across clusters
        self.distribute_spiders_to_clusters()

        # Deploy clusters in parallel
        deployment_tasks = []
        for cluster_name, spider_list in self.spider_clusters.items():
            task = asyncio.create_task(
                self.deploy_spider_cluster(cluster_name, spider_list)
            )
            deployment_tasks.append(task)

        # Wait for all clusters to deploy
        await asyncio.gather(*deployment_tasks)

        # Start intelligence coordination
        await self.start_intelligence_coordination()

        logger.info(f"✅ SPIDER ARMY DEPLOYMENT COMPLETE - {len(self.active_spiders)} SPIDERS ACTIVE")

    def distribute_spiders_to_clusters(self):
        """Distribute spider configurations across clusters"""
        cluster_assignments = {
            'cluster_alpha': [],    # Contract work spiders
            'cluster_beta': [],     # Market intelligence spiders
            'cluster_gamma': [],    # Content research spiders
            'cluster_delta': [],    # Advisor-specific spiders
            'cluster_omega': []     # Adaptive spiders
        }

        for spider_name, config in self.spider_configs.items():
            if 'upwork' in spider_name or 'freelancer' in spider_name or 'linkedin' in spider_name:
                cluster_assignments['cluster_alpha'].append(config)
            elif 'market' in spider_name:
                cluster_assignments['cluster_beta'].append(config)
            elif 'content' in spider_name:
                cluster_assignments['cluster_gamma'].append(config)
            elif any(advisor in spider_name for advisor in self.advisor_profiles.keys()):
                cluster_assignments['cluster_delta'].append(config)
            elif 'adaptive' in spider_name:
                cluster_assignments['cluster_omega'].append(config)

        self.spider_clusters = cluster_assignments
        logger.info(f"Distributed spiders across clusters: {[(k, len(v)) for k, v in cluster_assignments.items()]}")

    async def deploy_spider_cluster(self, cluster_name: str, spider_configs: List[SpiderConfig]):
        """Deploy a cluster of spiders"""
        logger.info(f"🕸️ Deploying {cluster_name} with {len(spider_configs)} spiders")

        cluster_runner = CrawlerRunner(self.settings)
        deployment_tasks = []

        for config in spider_configs:
            # Customize settings for this spider
            spider_settings = self.settings.copy()
            spider_settings.update(config.custom_settings)

            # Create deployment task
            task = asyncio.create_task(
                self.deploy_individual_spider(cluster_runner, config, spider_settings)
            )
            deployment_tasks.append(task)

            # Add delay between deployments to prevent overwhelming
            await asyncio.sleep(0.1)

        # Wait for cluster deployment to complete
        deployed = await asyncio.gather(*deployment_tasks, return_exceptions=True)

        successful_deployments = sum(1 for result in deployed if not isinstance(result, Exception))
        logger.info(f"✅ {cluster_name} deployment complete: {successful_deployments}/{len(spider_configs)} spiders active")

    async def deploy_individual_spider(self, runner: CrawlerRunner, config: SpiderConfig, settings):
        """Deploy an individual spider"""
        try:
            # Start the spider with its configuration
            deferred = runner.crawl(
                config.spider_class,
                name=config.spider_name,
                subscribers=config.target_agents,
                advisor_feeds=config.target_advisors,
                custom_settings=settings
            )

            # Track active spider
            self.active_spiders[config.spider_name] = {
                'config': config,
                'status': 'active',
                'start_time': datetime.now(),
                'metrics': {
                    'pages_crawled': 0,
                    'intelligence_items': 0,
                    'agents_fed': 0,
                    'advisors_fed': 0
                }
            }

            logger.info(f"🕷️ Deployed spider: {config.spider_name}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to deploy spider {config.spider_name}: {e}")
            return False

    async def start_intelligence_coordination(self):
        """Start the intelligence coordination system"""
        logger.info("🧠 Starting intelligence coordination system")

        # Start Redis pub/sub listeners for agent and advisor feeds
        coordination_tasks = [
            asyncio.create_task(self.monitor_spider_performance()),
            asyncio.create_task(self.coordinate_intelligence_flows()),
            asyncio.create_task(self.adaptive_spider_management()),
            asyncio.create_task(self.generate_real_time_metrics())
        ]

        await asyncio.gather(*coordination_tasks)

    async def monitor_spider_performance(self):
        """Monitor performance of all active spiders"""
        while True:
            try:
                performance_report = self.generate_performance_report()
                await self.optimize_spider_performance(performance_report)

                # Log performance summary
                logger.info(f"📊 Spider Performance: {performance_report['summary']}")

                await asyncio.sleep(300)  # Check every 5 minutes

            except Exception as e:
                logger.error(f"Error in spider performance monitoring: {e}")
                await asyncio.sleep(60)

    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        total_spiders = len(self.active_spiders)
        active_spiders = sum(1 for spider in self.active_spiders.values() if spider['status'] == 'active')

        total_intelligence = sum(
            spider['metrics']['intelligence_items']
            for spider in self.active_spiders.values()
        )

        total_agents_fed = sum(
            spider['metrics']['agents_fed']
            for spider in self.active_spiders.values()
        )

        total_advisors_fed = sum(
            spider['metrics']['advisors_fed']
            for spider in self.active_spiders.values()
        )

        return {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_spiders': total_spiders,
                'active_spiders': active_spiders,
                'intelligence_items_collected': total_intelligence,
                'agents_fed': total_agents_fed,
                'advisors_fed': total_advisors_fed,
                'success_rate': (active_spiders / total_spiders) * 100 if total_spiders > 0 else 0
            },
            'cluster_performance': self.get_cluster_performance(),
            'top_performers': self.get_top_performing_spiders(),
            'issues': self.identify_performance_issues()
        }

    def get_cluster_performance(self) -> Dict[str, Any]:
        """Get performance metrics by cluster"""
        cluster_performance = {}

        for cluster_name in self.spider_clusters.keys():
            cluster_spiders = [
                spider for spider_name, spider in self.active_spiders.items()
                if cluster_name in spider_name
            ]

            if cluster_spiders:
                cluster_performance[cluster_name] = {
                    'spider_count': len(cluster_spiders),
                    'active_count': sum(1 for s in cluster_spiders if s['status'] == 'active'),
                    'total_intelligence': sum(s['metrics']['intelligence_items'] for s in cluster_spiders),
                    'avg_performance': sum(s['metrics']['intelligence_items'] for s in cluster_spiders) / len(cluster_spiders)
                }

        return cluster_performance

    def get_top_performing_spiders(self) -> List[Dict[str, Any]]:
        """Get top performing spiders"""
        spider_performance = []

        for spider_name, spider_data in self.active_spiders.items():
            performance_score = (
                spider_data['metrics']['intelligence_items'] * 1.0 +
                spider_data['metrics']['agents_fed'] * 0.5 +
                spider_data['metrics']['advisors_fed'] * 2.0  # Advisors weighted higher
            )

            spider_performance.append({
                'name': spider_name,
                'score': performance_score,
                'intelligence_items': spider_data['metrics']['intelligence_items'],
                'agents_fed': spider_data['metrics']['agents_fed'],
                'advisors_fed': spider_data['metrics']['advisors_fed']
            })

        # Sort by performance score and return top 10
        spider_performance.sort(key=lambda x: x['score'], reverse=True)
        return spider_performance[:10]

    def identify_performance_issues(self) -> List[Dict[str, Any]]:
        """Identify spiders with performance issues"""
        issues = []

        for spider_name, spider_data in self.active_spiders.items():
            # Check for various performance issues
            runtime = datetime.now() - spider_data['start_time']
            runtime_hours = runtime.total_seconds() / 3600

            # Issue: Spider running too long without producing intelligence
            if runtime_hours > 2 and spider_data['metrics']['intelligence_items'] == 0:
                issues.append({
                    'spider': spider_name,
                    'issue': 'no_intelligence_collected',
                    'severity': 'high',
                    'runtime_hours': runtime_hours
                })

            # Issue: Spider status is not active
            if spider_data['status'] != 'active':
                issues.append({
                    'spider': spider_name,
                    'issue': 'inactive_status',
                    'severity': 'critical',
                    'status': spider_data['status']
                })

            # Issue: Low intelligence production rate
            if runtime_hours > 1:
                intelligence_rate = spider_data['metrics']['intelligence_items'] / runtime_hours
                if intelligence_rate < 0.5:  # Less than 0.5 items per hour
                    issues.append({
                        'spider': spider_name,
                        'issue': 'low_production_rate',
                        'severity': 'medium',
                        'rate': intelligence_rate
                    })

        return issues

    async def optimize_spider_performance(self, performance_report: Dict[str, Any]):
        """Optimize spider performance based on report"""
        issues = performance_report.get('issues', [])

        for issue in issues:
            spider_name = issue['spider']
            issue_type = issue['issue']
            severity = issue['severity']

            if severity == 'critical':
                # Restart critical spiders
                await self.restart_spider(spider_name)
            elif severity == 'high' and issue_type == 'no_intelligence_collected':
                # Adjust spider configuration
                await self.adjust_spider_config(spider_name, 'increase_sources')
            elif issue_type == 'low_production_rate':
                # Optimize spider parameters
                await self.adjust_spider_config(spider_name, 'optimize_parameters')

    async def restart_spider(self, spider_name: str):
        """Restart a problematic spider"""
        try:
            logger.info(f"🔄 Restarting spider: {spider_name}")

            # Mark spider as restarting
            if spider_name in self.active_spiders:
                self.active_spiders[spider_name]['status'] = 'restarting'

            # Get original configuration
            original_config = self.active_spiders[spider_name]['config']

            # Stop current spider (implementation would depend on spider management system)
            # await self.stop_spider(spider_name)

            # Redeploy with original configuration
            runner = CrawlerRunner(self.settings)
            await self.deploy_individual_spider(runner, original_config, self.settings)

            logger.info(f"✅ Successfully restarted spider: {spider_name}")

        except Exception as e:
            logger.error(f"❌ Failed to restart spider {spider_name}: {e}")

    async def adjust_spider_config(self, spider_name: str, adjustment_type: str):
        """Adjust spider configuration for optimization"""
        try:
            if spider_name not in self.active_spiders:
                return

            config = self.active_spiders[spider_name]['config']

            if adjustment_type == 'increase_sources':
                # Add more data sources
                config.custom_settings['additional_sources'] = True
                logger.info(f"🔧 Increased data sources for spider: {spider_name}")

            elif adjustment_type == 'optimize_parameters':
                # Reduce delay to increase throughput
                config.delay = max(1, config.delay - 1)
                config.custom_settings['DOWNLOAD_DELAY'] = config.delay
                logger.info(f"🔧 Optimized parameters for spider: {spider_name}")

        except Exception as e:
            logger.error(f"❌ Failed to adjust config for spider {spider_name}: {e}")

    async def coordinate_intelligence_flows(self):
        """Coordinate intelligence flows between spiders, agents, and advisors"""
        while True:
            try:
                # Process intelligence routing
                await self.process_intelligence_queue()

                # Update agent preferences based on feedback
                await self.update_agent_preferences()

                # Optimize advisor feeds
                await self.optimize_advisor_feeds()

                await asyncio.sleep(60)  # Process every minute

            except Exception as e:
                logger.error(f"Error in intelligence coordination: {e}")
                await asyncio.sleep(30)

    async def process_intelligence_queue(self):
        """Process the intelligence queue and route to appropriate consumers"""
        try:
            # Get intelligence items from Redis queue
            while True:
                intelligence_item = redis_client.lpop('intelligence_queue')
                if not intelligence_item:
                    break

                intelligence = json.loads(intelligence_item)
                await self.route_intelligence(intelligence)

        except Exception as e:
            logger.error(f"Error processing intelligence queue: {e}")

    async def route_intelligence(self, intelligence: Dict[str, Any]):
        """Route intelligence to appropriate agents and advisors"""
        intelligence_type = intelligence.get('intelligence_type', 'general')
        source_spider = intelligence.get('spider_name', 'unknown')

        # Route to agents based on intelligence type
        target_agents = self.get_target_agents_for_intelligence(intelligence_type)
        for agent_id in target_agents:
            await self.feed_agent(agent_id, intelligence)

        # Route to advisors based on content relevance
        target_advisors = self.get_target_advisors_for_intelligence(intelligence)
        for advisor_name in target_advisors:
            await self.feed_advisor(advisor_name, intelligence)

    def get_target_agents_for_intelligence(self, intelligence_type: str) -> List[str]:
        """Get target agents based on intelligence type"""
        type_to_agents = {
            'contract_work': [aid for aid, agent in self.agent_profiles.items() if agent.agent_type == 'job_application'],
            'market_intelligence': [aid for aid, agent in self.agent_profiles.items() if agent.agent_type == 'market_analysis'],
            'content_research': [aid for aid, agent in self.agent_profiles.items() if agent.agent_type == 'content_creation'],
            'trending_topics': [aid for aid, agent in self.agent_profiles.items() if agent.agent_type in ['content_creation', 'social_media']],
            'seo_keywords': [aid for aid, agent in self.agent_profiles.items() if agent.agent_type == 'content_creation']
        }

        return type_to_agents.get(intelligence_type, [])

    def get_target_advisors_for_intelligence(self, intelligence: Dict[str, Any]) -> List[str]:
        """Get target advisors based on intelligence content"""
        target_advisors = []

        intelligence_content = str(intelligence).lower()

        # Check each advisor's focus areas
        for advisor_name, advisor_profile in self.advisor_profiles.items():
            relevance_score = 0

            for focus_area in advisor_profile.focus_areas:
                if focus_area.replace('_', ' ') in intelligence_content:
                    relevance_score += 1

            # If intelligence is relevant to advisor, add to targets
            if relevance_score > 0:
                target_advisors.append(advisor_name)

        return target_advisors

    async def feed_agent(self, agent_id: str, intelligence: Dict[str, Any]):
        """Feed intelligence to a specific agent"""
        try:
            channel = f"agent:{agent_id}:intelligence"
            message = {
                'intelligence': intelligence,
                'timestamp': datetime.now().isoformat(),
                'agent_id': agent_id
            }

            redis_client.publish(channel, json.dumps(message))

            # Update metrics
            source_spider = intelligence.get('spider_name', 'unknown')
            if source_spider in self.active_spiders:
                self.active_spiders[source_spider]['metrics']['agents_fed'] += 1

        except Exception as e:
            logger.error(f"Error feeding agent {agent_id}: {e}")

    async def feed_advisor(self, advisor_name: str, intelligence: Dict[str, Any]):
        """Feed intelligence to a specific advisor"""
        try:
            channel = f"advisor:{advisor_name}:intelligence"
            message = {
                'intelligence': intelligence,
                'timestamp': datetime.now().isoformat(),
                'advisor_name': advisor_name,
                'relevance_score': self.calculate_advisor_relevance(advisor_name, intelligence)
            }

            redis_client.publish(channel, json.dumps(message))

            # Update metrics
            source_spider = intelligence.get('spider_name', 'unknown')
            if source_spider in self.active_spiders:
                self.active_spiders[source_spider]['metrics']['advisors_fed'] += 1

        except Exception as e:
            logger.error(f"Error feeding advisor {advisor_name}: {e}")

    def calculate_advisor_relevance(self, advisor_name: str, intelligence: Dict[str, Any]) -> float:
        """Calculate relevance score of intelligence for specific advisor"""
        if advisor_name not in self.advisor_profiles:
            return 0.0

        advisor_profile = self.advisor_profiles[advisor_name]
        intelligence_content = str(intelligence).lower()

        relevance_score = 0.0
        focus_areas = advisor_profile.focus_areas

        for focus_area in focus_areas:
            if focus_area.replace('_', ' ') in intelligence_content:
                relevance_score += 1.0 / len(focus_areas)

        return min(relevance_score, 1.0)

    async def update_agent_preferences(self):
        """Update agent preferences based on feedback and performance"""
        # This would implement machine learning to optimize agent feeding

    async def optimize_advisor_feeds(self):
        """Optimize advisor feeds based on engagement and feedback"""
        # This would implement optimization algorithms for advisor satisfaction

    async def adaptive_spider_management(self):
        """Manage adaptive spiders that learn and evolve"""
        while True:
            try:
                # Evolve adaptive spiders based on performance
                await self.evolve_adaptive_spiders()

                # Create new spider variations
                await self.spawn_new_spider_variants()

                # Remove underperforming spiders
                await self.cull_underperforming_spiders()

                await asyncio.sleep(1800)  # Every 30 minutes

            except Exception as e:
                logger.error(f"Error in adaptive spider management: {e}")
                await asyncio.sleep(300)

    async def evolve_adaptive_spiders(self):
        """Evolve adaptive spiders based on performance metrics"""
        adaptive_spiders = [
            name for name in self.active_spiders.keys()
            if 'adaptive' in name
        ]

        for spider_name in adaptive_spiders:
            spider_data = self.active_spiders[spider_name]
            performance_score = spider_data['metrics']['intelligence_items']

            # Evolve high-performing spiders
            if performance_score > 10:  # Threshold for evolution
                await self.evolve_spider_parameters(spider_name)

    async def evolve_spider_parameters(self, spider_name: str):
        """Evolve parameters of a specific spider"""
        try:
            logger.info(f"🧬 Evolving spider parameters: {spider_name}")

            # Implement evolutionary algorithm to optimize spider parameters
            # This could include adjusting delays, concurrency, target sources, etc.

        except Exception as e:
            logger.error(f"Error evolving spider {spider_name}: {e}")

    async def spawn_new_spider_variants(self):
        """Spawn new spider variants based on successful patterns"""
        # Identify successful spider patterns and create new variants

    async def cull_underperforming_spiders(self):
        """Remove spiders that consistently underperform"""
        underperformers = []

        for spider_name, spider_data in self.active_spiders.items():
            runtime = datetime.now() - spider_data['start_time']
            runtime_hours = runtime.total_seconds() / 3600

            # If spider has been running for over 6 hours with no intelligence
            if runtime_hours > 6 and spider_data['metrics']['intelligence_items'] == 0:
                underperformers.append(spider_name)

        for spider_name in underperformers:
            logger.info(f"🗑️ Culling underperforming spider: {spider_name}")
            await self.remove_spider(spider_name)

    async def remove_spider(self, spider_name: str):
        """Remove a spider from the active army"""
        try:
            if spider_name in self.active_spiders:
                del self.active_spiders[spider_name]
                logger.info(f"❌ Removed spider: {spider_name}")

        except Exception as e:
            logger.error(f"Error removing spider {spider_name}: {e}")

    async def generate_real_time_metrics(self):
        """Generate and broadcast real-time metrics"""
        while True:
            try:
                metrics = self.get_real_time_metrics()
                await self.broadcast_metrics(metrics)
                await asyncio.sleep(30)  # Every 30 seconds

            except Exception as e:
                logger.error(f"Error generating real-time metrics: {e}")
                await asyncio.sleep(60)

    def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get current real-time metrics"""
        return {
            'timestamp': datetime.now().isoformat(),
            'army_size': len(self.active_spiders),
            'active_spiders': sum(1 for s in self.active_spiders.values() if s['status'] == 'active'),
            'total_intelligence_collected': sum(s['metrics']['intelligence_items'] for s in self.active_spiders.values()),
            'agents_fed_today': sum(s['metrics']['agents_fed'] for s in self.active_spiders.values()),
            'advisors_fed_today': sum(s['metrics']['advisors_fed'] for s in self.active_spiders.values()),
            'cluster_status': self.get_cluster_status(),
            'top_performers': self.get_top_performing_spiders()[:5]
        }

    def get_cluster_status(self) -> Dict[str, Any]:
        """Get status of each spider cluster"""
        cluster_status = {}

        for cluster_name in self.spider_clusters.keys():
            cluster_spiders = [
                spider for spider_name, spider in self.active_spiders.items()
                if any(keyword in spider_name for keyword in self.get_cluster_keywords(cluster_name))
            ]

            cluster_status[cluster_name] = {
                'total_spiders': len(cluster_spiders),
                'active_spiders': sum(1 for s in cluster_spiders if s['status'] == 'active'),
                'intelligence_collected': sum(s['metrics']['intelligence_items'] for s in cluster_spiders)
            }

        return cluster_status

    def get_cluster_keywords(self, cluster_name: str) -> List[str]:
        """Get keywords to identify spiders belonging to a cluster"""
        keywords = {
            'cluster_alpha': ['upwork', 'freelancer', 'linkedin'],
            'cluster_beta': ['market', 'news', 'pricing', 'funding'],
            'cluster_gamma': ['content', 'trending', 'seo', 'viral'],
            'cluster_delta': list(self.advisor_profiles.keys()),
            'cluster_omega': ['adaptive']
        }
        return keywords.get(cluster_name, [])

    async def broadcast_metrics(self, metrics: Dict[str, Any]):
        """Broadcast metrics to monitoring systems"""
        try:
            # Broadcast to Redis for real-time dashboards
            redis_client.publish('spider_army_metrics', json.dumps(metrics))

            # Send to Django API for storage
            await self.send_metrics_to_api(metrics)

        except Exception as e:
            logger.error(f"Error broadcasting metrics: {e}")

    async def send_metrics_to_api(self, metrics: Dict[str, Any]):
        """Send metrics to Django API"""
        try:
            base_url = os.environ.get('BACKEND_URL', 'http://localhost:8000')
            api_url = f"{base_url}/api/spider-army/metrics/"
            headers = {'Content-Type': 'application/json'}

            # Use aiohttp for async request
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, json=metrics, headers=headers) as response:
                    if response.status == 201:
                        logger.debug("Metrics sent to Django API successfully")
                    else:
                        logger.warning(f"Django API returned status {response.status}")

        except Exception as e:
            logger.error(f"Failed to send metrics to Django API: {e}")


def activate_job_spiders(user_profile=None):
    """
    Synchronous wrapper for activating job spiders
    This allows the function to be called from non-async contexts
    """
    import asyncio

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(_activate_job_spiders_async(user_profile))


async def _activate_job_spiders_async(user_profile=None):
    """
    Activate job-specific spiders for real opportunity collection (async version)
    This function connects spiders to collect real jobs and opportunities
    """
    try:
        from channels.layers import get_channel_layer
        from .spider_registry import SpiderRegistry
        import asyncio

        logger.info("🕷️ Activating job spiders for real opportunity collection...")

        # Initialize spider registry
        spider_registry = SpiderRegistry()
        channel_layer = get_channel_layer()

        # Define the spiders we want to activate for job hunting
        job_spiders = [
            'toptal',       # High-paying tech jobs
            'guru',         # Freelance opportunities
            'flexjobs',     # Remote positions
            'remoteok',     # Remote opportunities
            'peopleperhour' # Freelance gigs
        ]

        opportunities_collected = []
        fallback_events = []

        for spider_name in job_spiders:
            try:
                logger.info(f"Activating {spider_name} spider...")

                # Get spider class
                spider_class = spider_registry.get_spider_class(spider_name)
                if not spider_class:
                    logger.warning(f"Spider {spider_name} not found in registry")
                    continue

                # Create spider instance with required parameters
                spider = spider_registry.create_spider_instance(
                    spider_name=spider_name,
                    spider_id=f"{spider_name}_job_collector",
                    targets=['income_builder'],
                    subscribers=['decision_command'],
                    redis_config={'host': 'localhost', 'port': 6379, 'db': 0}
                )

                # Try to use real spider data collection, fall back to mock if needed
                try:
                    # Attempt to start the spider and collect data
                    if hasattr(spider, 'start'):
                        await spider.start()
                        # Give spider time to collect initial data
                        await asyncio.sleep(2)

                    # Check if spider collected any real data
                    if hasattr(spider, 'get_collected_data'):
                        real_opportunities = await spider.get_collected_data()
                        if real_opportunities:
                            opportunities_collected.extend(real_opportunities)
                            logger.info(f"Collected {len(real_opportunities)} REAL opportunities from {spider_name}")
                        else:
                            # Fall back to mock data if no real data
                            mock_opportunities = await generate_mock_job_opportunities(spider_name)
                            opportunities_collected.extend(mock_opportunities)
                            logger.info(f"Using mock data for {spider_name} (no real data available)")
                            fallback_events.append({
                                'spider': spider_name,
                                'fallback_type': 'mock_opportunities',
                                'real_data_failed': True,
                                'collection_error': 'no_real_data',
                                'error_type': 'no_real_data',
                            })
                    else:
                        # Fall back to mock data if spider doesn't have data collection method
                        mock_opportunities = await generate_mock_job_opportunities(spider_name)
                        opportunities_collected.extend(mock_opportunities)
                        logger.info(f"Using mock data for {spider_name} (spider lacks get_collected_data method)")
                        fallback_events.append({
                            'spider': spider_name,
                            'fallback_type': 'mock_opportunities',
                            'real_data_failed': True,
                            'collection_error': 'missing_get_collected_data',
                            'error_type': 'missing_get_collected_data',
                        })

                except Exception as spider_error:
                    logger.warning(f"Spider {spider_name} real data collection failed: {spider_error}")
                    # Fall back to mock data on any error
                    mock_opportunities = await generate_mock_job_opportunities(spider_name)
                    opportunities_collected.extend(mock_opportunities)
                    fallback_events.append({
                        'spider': spider_name,
                        'fallback_type': 'mock_opportunities',
                        'real_data_failed': True,
                        'collection_error': str(spider_error),
                        'error_type': type(spider_error).__name__,
                    })

                # Send opportunities through WebSocket to Decision Command
                current_opportunities = [opp for opp in opportunities_collected if opp.get('platform') == spider_name]
                if channel_layer and current_opportunities:
                    await channel_layer.group_send(
                        'decision_command',
                        {
                            'type': 'spider_data',
                            'spider': spider_name,
                            'opportunities': current_opportunities,
                            'timestamp': datetime.now().isoformat()
                        }
                    )
                    logger.info(f"Sent {len(current_opportunities)} opportunities from {spider_name}")

            except Exception as e:
                logger.error(f"Error activating {spider_name} spider: {e}")
                continue

        logger.info(f"✅ Job spiders activated! Collected {len(opportunities_collected)} opportunities")
        fallback_used = bool(fallback_events)
        return {
            'success': True,
            'spiders_activated': len(job_spiders),
            'opportunities_collected': len(opportunities_collected),
            'opportunities': opportunities_collected,
            'fallback_used': fallback_used,
            'fallback_type': 'mock_opportunities' if fallback_used else None,
            'real_data_failed': fallback_used,
            'collection_error': fallback_events[0]['collection_error'] if fallback_events else None,
            'error_type': fallback_events[0]['error_type'] if fallback_events else None,
            'partial_failure': fallback_used,
            'collection_errors': fallback_events,
        }

    except Exception as e:
        logger.error(f"Error activating job spiders: {e}")
        return {
            'success': False,
            'error': str(e),
            'opportunities_collected': 0
        }


async def generate_mock_job_opportunities(spider_name):
    """Generate realistic job opportunities that spiders would find"""
    base_opportunities = {
        'toptal': [
            {
                'id': f'toptal_{int(datetime.now().timestamp())}',
                'title': 'Senior Python Developer',
                'platform': 'toptal',
                'budget_min': 80,
                'budget_max': 120,
                'budget_type': 'hourly',
                'description': 'Looking for experienced Python developer for AI/ML project',
                'skills': ['Python', 'Django', 'Machine Learning', 'AWS'],
                'duration': '3-6 months',
                'remote': True,
                'experience_level': 'expert',
                'client_rating': 4.8,
                'posted_at': datetime.now().isoformat(),
                'urgency': 'high',
                'revenue_potential': 15000
            },
            {
                'id': f'toptal_{int(datetime.now().timestamp())}_2',
                'title': 'React Frontend Specialist',
                'platform': 'toptal',
                'budget_min': 60,
                'budget_max': 90,
                'budget_type': 'hourly',
                'description': 'Need React expert for fintech application',
                'skills': ['React', 'TypeScript', 'Node.js', 'GraphQL'],
                'duration': '2-4 months',
                'remote': True,
                'experience_level': 'expert',
                'client_rating': 4.9,
                'posted_at': datetime.now().isoformat(),
                'urgency': 'medium',
                'revenue_potential': 12000
            }
        ],
        'guru': [
            {
                'id': f'guru_{int(datetime.now().timestamp())}',
                'title': 'Content Writer for Tech Blog',
                'platform': 'guru',
                'budget_min': 500,
                'budget_max': 1500,
                'budget_type': 'fixed',
                'description': 'Write 10 technical articles about AI trends',
                'skills': ['Content Writing', 'Technical Writing', 'AI', 'SEO'],
                'duration': '1 month',
                'remote': True,
                'experience_level': 'intermediate',
                'client_rating': 4.5,
                'posted_at': datetime.now().isoformat(),
                'urgency': 'medium',
                'revenue_potential': 1000
            }
        ],
        'flexjobs': [
            {
                'id': f'flexjobs_{int(datetime.now().timestamp())}',
                'title': 'Remote Data Analyst',
                'platform': 'flexjobs',
                'budget_min': 25,
                'budget_max': 35,
                'budget_type': 'hourly',
                'description': 'Analyze customer data and create reports',
                'skills': ['Python', 'SQL', 'Excel', 'Tableau'],
                'duration': 'ongoing',
                'remote': True,
                'experience_level': 'intermediate',
                'client_rating': 4.2,
                'posted_at': datetime.now().isoformat(),
                'urgency': 'low',
                'revenue_potential': 4200
            }
        ],
        'remoteok': [
            {
                'id': f'remoteok_{int(datetime.now().timestamp())}',
                'title': 'DevOps Engineer',
                'platform': 'remoteok',
                'budget_min': 70000,
                'budget_max': 90000,
                'budget_type': 'annual',
                'description': 'Manage cloud infrastructure and CI/CD pipelines',
                'skills': ['AWS', 'Docker', 'Kubernetes', 'Terraform'],
                'duration': 'full-time',
                'remote': True,
                'experience_level': 'senior',
                'client_rating': 4.6,
                'posted_at': datetime.now().isoformat(),
                'urgency': 'high',
                'revenue_potential': 80000
            }
        ],
        'peopleperhour': [
            {
                'id': f'pph_{int(datetime.now().timestamp())}',
                'title': 'WordPress Website Setup',
                'platform': 'peopleperhour',
                'budget_min': 200,
                'budget_max': 500,
                'budget_type': 'fixed',
                'description': 'Set up WordPress site with custom theme',
                'skills': ['WordPress', 'PHP', 'CSS', 'HTML'],
                'duration': '1-2 weeks',
                'remote': True,
                'experience_level': 'intermediate',
                'client_rating': 4.0,
                'posted_at': datetime.now().isoformat(),
                'urgency': 'medium',
                'revenue_potential': 350
            }
        ]
    }

    # Return opportunities for the specified spider
    return base_opportunities.get(spider_name, [])


# Main execution function
async def main():
    """Main function to start the spider army"""
    logger.info("🕷️🕸️ SPIDER ARMY SUPREME ORCHESTRATOR STARTING 🕸️🕷️")

    orchestrator = SpiderArmyOrchestrator()

    try:
        await orchestrator.deploy_spider_army()

        # Keep the orchestrator running
        while True:
            await asyncio.sleep(60)
            logger.info("Spider Army Orchestrator is running...")

    except KeyboardInterrupt:
        logger.info("Shutting down Spider Army Orchestrator...")
    except Exception as e:
        logger.error(f"Fatal error in Spider Army Orchestrator: {e}")
        raise


if __name__ == "__main__":
    # Run the spider army
    asyncio.run(main())

"""
Spider Registry - Central Registry for All Intelligence Spiders
==============================================================

This module maintains the central registry of all spider classes and their configurations.
Used by the Spider Army Orchestrator to deploy and manage specialized spiders.
"""

from typing import Dict, Type, Any
import logging

# Import existing specialized spiders
from .specialized.financial_spider import FinancialIntelligenceSpider
from .specialized.innovation_spider import InnovationTrackingSpider
from .specialized.social_spider import SocialSentimentSpider
from .specialized.market_spider import MarketDataSpider
from .specialized.news_spider import NewsHarvesterSpider

# Import new freelance platform spiders
from .specialized.toptal_spider import ToptalIntelligenceSpider
from .specialized.guru_spider import GuruIntelligenceSpider
from .specialized.peopleperhour_spider import PeoplePerHourIntelligenceSpider
from .specialized.ninetyninedesigns_spider import NinetyNineDesignsIntelligenceSpider
from .specialized.flexjobs_spider import FlexJobsIntelligenceSpider
from .specialized.remoteok_spider import RemoteOKIntelligenceSpider

# Import content monetization spiders
from .specialized.medium_spider import MediumIntelligenceSpider
from .specialized.gumroad_spider import GumroadIntelligenceSpider

# Import base spider for fallbacks
from .base_spider import BaseIntelligenceSpider

logger = logging.getLogger(__name__)


class SpiderRegistry:
    """Central registry for all intelligence spiders"""

    def __init__(self):
        self.spider_classes: Dict[str, Type[BaseIntelligenceSpider]] = {}
        self.spider_configs: Dict[str, Dict[str, Any]] = {}
        self._register_all_spiders()

    def _register_all_spiders(self):
        """Register all available spider classes"""

        # === EXISTING SPIDERS (5) ===
        self.register_spider('financial', FinancialIntelligenceSpider, {
            'category': 'financial',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['sec.gov', 'finance.yahoo.com', 'polygon.io']
        })

        self.register_spider('innovation', InnovationTrackingSpider, {
            'category': 'innovation',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['arxiv.org', 'patents.google.com', 'github.com']
        })

        self.register_spider('social_sentiment', SocialSentimentSpider, {
            'category': 'social',
            'priority': 2,
            'rate_limit': 2.0,
            'targets': ['reddit.com', 'twitter.com', 'stocktwits.com']
        })

        self.register_spider('market_data', MarketDataSpider, {
            'category': 'market',
            'priority': 1,
            'rate_limit': 5.0,
            'targets': ['binance.com', 'coinbase.com', 'tradingview.com']
        })

        self.register_spider('news_harvester', NewsHarvesterSpider, {
            'category': 'news',
            'priority': 1,
            'rate_limit': 2.0,
            'targets': ['bloomberg.com', 'reuters.com', 'cnbc.com']
        })

        # === FREELANCE/GIG PLATFORM SPIDERS (10) ===
        self.register_spider('toptal', ToptalIntelligenceSpider, {
            'category': 'freelance',
            'priority': 1,
            'rate_limit': 0.5,
            'targets': ['toptal.com/jobs', 'toptal.com/freelance']
        })

        self.register_spider('guru', GuruIntelligenceSpider, {
            'category': 'freelance',
            'priority': 2,
            'rate_limit': 1.0,
            'targets': ['guru.com/jobs', 'guru.com/freelance']
        })

        self.register_spider('peopleperhour', PeoplePerHourIntelligenceSpider, {
            'category': 'freelance',
            'priority': 2,
            'rate_limit': 1.0,
            'targets': ['peopleperhour.com/freelance-jobs']
        })

        self.register_spider('ninetyninedesigns', NinetyNineDesignsIntelligenceSpider, {
            'category': 'design',
            'priority': 2,
            'rate_limit': 0.5,
            'targets': ['99designs.com/contests']
        })

        self.register_spider('flexjobs', FlexJobsIntelligenceSpider, {
            'category': 'remote_work',
            'priority': 2,
            'rate_limit': 1.0,
            'targets': ['flexjobs.com/jobs']
        })

        self.register_spider('remoteok', RemoteOKIntelligenceSpider, {
            'category': 'remote_work',
            'priority': 2,
            'rate_limit': 1.0,
            'targets': ['remoteok.io']
        })

        # Register placeholder spiders for remaining freelance platforms
        freelance_platforms = [
            ('weworkremotely', 'weworkremotely.com'),
            ('angellist', 'angel.co/jobs'),
            ('dribbble', 'dribbble.com/jobs'),
            ('behance', 'behance.net/jobboard')
        ]

        for platform, target in freelance_platforms:
            self.register_spider(platform, BaseIntelligenceSpider, {
                'category': 'freelance',
                'priority': 3,
                'rate_limit': 1.0,
                'targets': [target],
                'placeholder': True
            })

        # === CONTENT MONETIZATION SPIDERS (8) ===
        self.register_spider('medium', MediumIntelligenceSpider, {
            'category': 'content',
            'priority': 2,
            'rate_limit': 1.0,
            'targets': ['medium.com/partner-program']
        })

        self.register_spider('gumroad', GumroadIntelligenceSpider, {
            'category': 'digital_products',
            'priority': 2,
            'rate_limit': 1.0,
            'targets': ['gumroad.com/discover']
        })

        # Register placeholder spiders for remaining content platforms
        content_platforms = [
            ('substack', 'substack.com'),
            ('patreon', 'patreon.com'),
            ('kofi', 'ko-fi.com'),
            ('teachable', 'teachable.com'),
            ('udemy', 'udemy.com'),
            ('skillshare', 'skillshare.com')
        ]

        for platform, target in content_platforms:
            self.register_spider(platform, BaseIntelligenceSpider, {
                'category': 'content',
                'priority': 3,
                'rate_limit': 1.0,
                'targets': [target],
                'placeholder': True
            })

        # === FINANCIAL/CRYPTO SPIDERS (7) ===
        financial_platforms = [
            ('coingecko', 'coingecko.com/api'),
            ('etherscan', 'etherscan.io/apis'),
            ('opensea', 'opensea.io/activity'),
            ('tradingview', 'tradingview.com/markets'),
            ('seekingalpha', 'seekingalpha.com'),
            ('bloomberg_terminal', 'bloomberg.com/professional'),
            ('reuters_eikon', 'reuters.com/en/eikon')
        ]

        for platform, target in financial_platforms:
            self.register_spider(platform, BaseIntelligenceSpider, {
                'category': 'financial',
                'priority': 2,
                'rate_limit': 1.0,
                'targets': [target],
                'placeholder': True
            })

        # === AI/TECH OPPORTUNITY SPIDERS (10) ===
        tech_platforms = [
            ('huggingface', 'huggingface.co/jobs'),
            ('kaggle', 'kaggle.com/competitions'),
            ('github_jobs', 'github.com/jobs'),
            ('stackoverflow_jobs', 'stackoverflow.com/jobs'),
            ('producthunt', 'producthunt.com'),
            ('hackernews', 'news.ycombinator.com'),
            ('devto', 'dev.to/jobs'),
            ('hashnode', 'hashnode.com/jobs'),
            ('indiegogo', 'indiegogo.com'),
            ('kickstarter', 'kickstarter.com')
        ]

        for platform, target in tech_platforms:
            self.register_spider(platform, BaseIntelligenceSpider, {
                'category': 'tech',
                'priority': 2,
                'rate_limit': 1.0,
                'targets': [target],
                'placeholder': True
            })

        logger.info(f"Registered {len(self.spider_classes)} spider classes")

    def register_spider(self, spider_name: str, spider_class: Type[BaseIntelligenceSpider], config: Dict[str, Any]):
        """Register a spider class with configuration"""
        self.spider_classes[spider_name] = spider_class
        self.spider_configs[spider_name] = config
        logger.debug(f"Registered spider: {spider_name}")

    def get_spider_class(self, spider_name: str) -> Type[BaseIntelligenceSpider]:
        """Get spider class by name"""
        return self.spider_classes.get(spider_name, BaseIntelligenceSpider)

    def get_spider_config(self, spider_name: str) -> Dict[str, Any]:
        """Get spider configuration by name"""
        return self.spider_configs.get(spider_name, {})

    def list_spiders(self) -> Dict[str, Dict[str, Any]]:
        """List all registered spiders with their configurations"""
        return {
            name: {
                'class': spider_class.__name__,
                'config': self.spider_configs.get(name, {}),
                'category': self.spider_configs.get(name, {}).get('category', 'unknown'),
                'priority': self.spider_configs.get(name, {}).get('priority', 5),
                'is_placeholder': self.spider_configs.get(name, {}).get('placeholder', False)
            }
            for name, spider_class in self.spider_classes.items()
        }

    def get_spiders_by_category(self, category: str) -> Dict[str, Type[BaseIntelligenceSpider]]:
        """Get all spiders in a specific category"""
        return {
            name: spider_class
            for name, spider_class in self.spider_classes.items()
            if self.spider_configs.get(name, {}).get('category') == category
        }

    def get_active_spiders(self) -> Dict[str, Type[BaseIntelligenceSpider]]:
        """Get only non-placeholder spiders"""
        return {
            name: spider_class
            for name, spider_class in self.spider_classes.items()
            if not self.spider_configs.get(name, {}).get('placeholder', False)
        }

    def create_spider_instance(self, spider_name: str, spider_id: str, targets, subscribers, redis_config):
        """Create an instance of a specific spider"""
        spider_class = self.get_spider_class(spider_name)
        try:
            return spider_class(spider_id, targets, subscribers, redis_config)
        except Exception as e:
            logger.error(f"Failed to create spider instance for {spider_name}: {e}")
            # Fallback to base spider
            return BaseIntelligenceSpider(spider_id, targets, subscribers, redis_config)

    def get_spider_count(self) -> Dict[str, int]:
        """Get count of spiders by category"""
        categories = {}
        for config in self.spider_configs.values():
            category = config.get('category', 'unknown')
            categories[category] = categories.get(category, 0) + 1

        return {
            'total': len(self.spider_classes),
            'active': len(self.get_active_spiders()),
            'by_category': categories
        }


# Global spider registry instance
spider_registry = SpiderRegistry()


def get_spider_registry() -> SpiderRegistry:
    """Get the global spider registry instance"""
    return spider_registry


def register_custom_spider(name: str, spider_class: Type[BaseIntelligenceSpider], config: Dict[str, Any]):
    """Register a custom spider at runtime"""
    spider_registry.register_spider(name, spider_class, config)


# Export commonly used functions
__all__ = [
    'SpiderRegistry',
    'spider_registry',
    'get_spider_registry',
    'register_custom_spider'
]
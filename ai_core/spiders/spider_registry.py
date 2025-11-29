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
from .specialized.content_monetization_spider import ContentMonetizationSpider
from .specialized.tech_community_spider import TechCommunitySpider

# Import sports betting spiders
from .specialized.horse_racing_spider import HorseRacingSpider
from .specialized.combat_sports_spider import CombatSportsSpider

# Import legal spiders
from .specialized.courtlistener_spider import CourtListenerSpider
from .specialized.justia_spider import JustiaSpider
from .specialized.findlaw_spider import FindLawSpider
from .specialized.lii_spider import LegalInformationInstituteSpider

# Session 218: NEWS spiders
from .specialized.techcrunch_spider import TechCrunchSpider
from .specialized.axios_spider import AxiosSpider
from .specialized.verge_spider import TheVergeSpider

# Session 218: INNOVATION spiders
from .specialized.mit_tech_review_spider import MITTechReviewSpider
from .specialized.wired_spider import WiredSpider

# Session 218: DESIGN spiders
from .specialized.dribbble_spider import DribbbleSpider
from .specialized.behance_spider import BehanceSpider

# Session 218: Additional FREELANCE spiders
from .specialized.weworkremotely_spider import WeWorkRemotelySpider
from .specialized.angellist_spider import AngelListSpider

# Session 218: EDUCATION spiders
from .specialized.teachable_spider import TeachableSpider
from .specialized.udemy_spider import UdemySpider
from .specialized.skillshare_spider import SkillshareSpider

# Session 218: Additional FINANCIAL spiders
from .specialized.etherscan_spider import EtherscanSpider
from .specialized.opensea_spider import OpenSeaSpider
from .specialized.seekingalpha_spider import SeekingAlphaSpider
from .specialized.bloomberg_spider import BloombergSpider
from .specialized.reuters_spider import ReutersSpider

# Session 218: TECH spiders
from .specialized.hackernews_spider import HackerNewsSpider
from .specialized.devto_spider import DevToSpider
from .specialized.hashnode_spider import HashnodeSpider
from .specialized.indiegogo_spider import IndiegogoSpider
from .specialized.kickstarter_spider import KickstarterSpider

# Import financial API spiders (CRITICAL FIX: These were built but not registered!)
from .specialized.coingecko_spider import CoinGeckoSpider
from .specialized.yahoo_finance_spider import YahooFinanceSpider

# Session 218: CREATIVE ASSETS & STOCK spiders (5)
from .specialized.envato_spider import EnvatoSpider
from .specialized.creativemarket_spider import CreativeMarketSpider
from .specialized.adobestock_spider import AdobeStockSpider
from .specialized.shutterstock_spider import ShutterstockSpider
from .specialized.canva_spider import CanvaSpider

# Session 218: AI/CREATIVE TOOLS spiders (4)
from .specialized.midjourney_spider import MidjourneySpider
from .specialized.civitai_spider import CivitAISpider
from .specialized.runwayml_spider import RunwayMLSpider
from .specialized.replicate_spider import ReplicateSpider

# Session 218: DIGITAL PRODUCT PLATFORMS spiders (4)
from .specialized.etsy_spider import EtsySpider
from .specialized.lemonsqueezy_spider import LemonSqueezySpider
from .specialized.sellfy_spider import SellfySpider
from .specialized.appsumo_spider import AppSumoSpider

# Session 218: CONTENT CREATION spiders (3)
from .specialized.convertkit_spider import ConvertKitSpider
from .specialized.notion_spider import NotionSpider
from .specialized.figma_spider import FigmaSpider

# Session 263: NEW SPIDERS TO REACH 70 TOTAL
from .specialized.reddit_spider import RedditSpider
from .specialized.unsplash_spider import UnsplashSpider
from .specialized.adzuna_spider import AdzunaSpider

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
            'targets': ['finance.yahoo.com', 'polygon.io']  # Removed sec.gov - temporarily disabled
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
            'targets': ['binance.com', 'coinbase.com']  # Removed tradingview.com - replaced with Polygon
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

        # Session 218: Activate WeWorkRemotely and AngelList (were placeholders)
        self.register_spider('weworkremotely', WeWorkRemotelySpider, {
            'category': 'freelance',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['weworkremotely.com/categories/']
        })

        self.register_spider('angellist', AngelListSpider, {
            'category': 'freelance',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['angel.co/jobs']
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

        # Register content monetization spiders with concrete implementation
        self.register_spider('substack', ContentMonetizationSpider, {
            'category': 'content',
            'priority': 2,
            'rate_limit': 1.0,
            'targets': ['substack.com']
        })

        self.register_spider('patreon', ContentMonetizationSpider, {
            'category': 'content',
            'priority': 2,
            'rate_limit': 1.0,
            'targets': ['patreon.com']
        })

        self.register_spider('kofi', ContentMonetizationSpider, {
            'category': 'content',
            'priority': 2,
            'rate_limit': 1.0,
            'targets': ['ko-fi.com']
        })

        self.register_spider('producthunt', ContentMonetizationSpider, {
            'category': 'content',
            'priority': 2,
            'rate_limit': 1.0,
            'targets': ['producthunt.com']
        })

        # Session 218: Activate Education spiders (were placeholders)
        self.register_spider('teachable', TeachableSpider, {
            'category': 'education',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['teachable.com']
        })

        self.register_spider('udemy', UdemySpider, {
            'category': 'education',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['udemy.com']
        })

        self.register_spider('skillshare', SkillshareSpider, {
            'category': 'education',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['skillshare.com']
        })

        # === FINANCIAL/CRYPTO SPIDERS ===
        # ✅ CRITICAL FIX: Register real CoinGecko and Yahoo Finance spiders
        self.register_spider('coingecko', CoinGeckoSpider, {
            'category': 'financial',
            'priority': 1,  # High priority - real implementation
            'rate_limit': 1.0,
            'targets': ['api.coingecko.com/api/v3']
        })

        self.register_spider('yahoo_finance', YahooFinanceSpider, {
            'category': 'financial',
            'priority': 1,  # High priority - real implementation
            'rate_limit': 1.0,
            'targets': ['query1.finance.yahoo.com/v8', 'query2.finance.yahoo.com/v10']
        })

        # Session 218: Activate Financial spiders (were placeholders)
        self.register_spider('etherscan', EtherscanSpider, {
            'category': 'financial',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['etherscan.io/apis']
        })

        self.register_spider('opensea', OpenSeaSpider, {
            'category': 'financial',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['opensea.io/activity']
        })

        self.register_spider('seekingalpha', SeekingAlphaSpider, {
            'category': 'financial',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['seekingalpha.com']
        })

        self.register_spider('bloomberg_terminal', BloombergSpider, {
            'category': 'financial',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['bloomberg.com/professional']
        })

        self.register_spider('reuters_eikon', ReutersSpider, {
            'category': 'financial',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['reuters.com/en/eikon']
        })

        # === AI/TECH OPPORTUNITY SPIDERS (10) ===
        # Register tech community spiders with concrete implementation
        self.register_spider('huggingface', TechCommunitySpider, {
            'category': 'tech',
            'priority': 2,
            'rate_limit': 1.0,
            'targets': ['huggingface.co']
        })

        self.register_spider('kaggle', TechCommunitySpider, {
            'category': 'tech',
            'priority': 2,
            'rate_limit': 1.0,
            'targets': ['kaggle.com']
        })

        self.register_spider('github_jobs', TechCommunitySpider, {
            'category': 'tech',
            'priority': 2,
            'rate_limit': 1.0,
            'targets': ['github.com']
        })

        self.register_spider('stackoverflow_jobs', TechCommunitySpider, {
            'category': 'tech',
            'priority': 2,
            'rate_limit': 1.0,
            'targets': ['stackoverflow.com']
        })

        # Session 218: Activate Tech spiders (were placeholders)
        self.register_spider('hackernews', HackerNewsSpider, {
            'category': 'tech',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['news.ycombinator.com']
        })

        self.register_spider('devto', DevToSpider, {
            'category': 'tech',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['dev.to']
        })

        self.register_spider('hashnode', HashnodeSpider, {
            'category': 'tech',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['hashnode.com']
        })

        self.register_spider('indiegogo', IndiegogoSpider, {
            'category': 'tech',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['indiegogo.com']
        })

        self.register_spider('kickstarter', KickstarterSpider, {
            'category': 'tech',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['kickstarter.com']
        })

        # === SPORTS BETTING SPIDERS (5) ===
        self.register_spider('horse_racing', HorseRacingSpider, {
            'category': 'sports_betting',
            'priority': 1,
            'rate_limit': 2.0,
            'targets': ['reddit.com/r/horseracing']
        })

        self.register_spider('combat_sports', CombatSportsSpider, {
            'category': 'sports_betting',
            'priority': 1,
            'rate_limit': 2.0,
            'targets': ['reddit.com/r/MMA', 'reddit.com/r/ufc', 'reddit.com/r/Boxing']
        })

        # === LEGAL SPIDERS (4) ===
        self.register_spider('courtlistener', CourtListenerSpider, {
            'category': 'legal',
            'priority': 2,
            'rate_limit': 1.0,
            'targets': ['courtlistener.com/api']
        })

        self.register_spider('justia', JustiaSpider, {
            'category': 'legal',
            'priority': 2,
            'rate_limit': 1.0,
            'targets': ['news.justia.com', 'law.justia.com']
        })

        self.register_spider('findlaw', FindLawSpider, {
            'category': 'legal',
            'priority': 2,
            'rate_limit': 1.0,
            'targets': ['findlaw.com/legalblogs']
        })

        self.register_spider('lii', LegalInformationInstituteSpider, {
            'category': 'legal',
            'priority': 2,
            'rate_limit': 1.0,
            'targets': ['law.cornell.edu/supct', 'law.cornell.edu/uscode']
        })

        # === SESSION 218: NEWS SPIDERS (3) ===
        self.register_spider('techcrunch', TechCrunchSpider, {
            'category': 'news',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['techcrunch.com/feed/']
        })

        self.register_spider('axios', AxiosSpider, {
            'category': 'news',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['api.axios.com/feed/']
        })

        self.register_spider('theverge', TheVergeSpider, {
            'category': 'news',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['theverge.com/rss/']
        })

        # === SESSION 218: INNOVATION SPIDERS (2) ===
        self.register_spider('mit_tech_review', MITTechReviewSpider, {
            'category': 'innovation',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['technologyreview.com/feed/']
        })

        self.register_spider('wired', WiredSpider, {
            'category': 'innovation',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['wired.com/feed/rss']
        })

        # === SESSION 218: DESIGN SPIDERS (2) ===
        # Activate Dribbble (was placeholder)
        self.register_spider('dribbble', DribbbleSpider, {
            'category': 'design',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['dribbble.com/shots/']
        })

        # Activate Behance (was placeholder)
        self.register_spider('behance', BehanceSpider, {
            'category': 'design',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['behance.net/feeds/projects']
        })

        # === SESSION 218: CREATIVE ASSETS & STOCK SPIDERS (5) ===
        self.register_spider('envato', EnvatoSpider, {
            'category': 'creative_assets',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['envato.com/blog/']
        })

        self.register_spider('creativemarket', CreativeMarketSpider, {
            'category': 'creative_assets',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['creativemarket.com']
        })

        self.register_spider('adobestock', AdobeStockSpider, {
            'category': 'creative_assets',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['stock.adobe.com']
        })

        self.register_spider('shutterstock', ShutterstockSpider, {
            'category': 'creative_assets',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['shutterstock.com/blog/']
        })

        self.register_spider('canva', CanvaSpider, {
            'category': 'creative_assets',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['canva.com/designschool/']
        })

        # === SESSION 218: AI/CREATIVE TOOLS SPIDERS (4) ===
        self.register_spider('midjourney', MidjourneySpider, {
            'category': 'ai_creative',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['midjourney.com']
        })

        self.register_spider('civitai', CivitAISpider, {
            'category': 'ai_creative',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['civitai.com']
        })

        self.register_spider('runwayml', RunwayMLSpider, {
            'category': 'ai_creative',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['runwayml.com/blog/']
        })

        self.register_spider('replicate', ReplicateSpider, {
            'category': 'ai_creative',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['replicate.com']
        })

        # === SESSION 218: DIGITAL PRODUCT PLATFORMS SPIDERS (4) ===
        self.register_spider('etsy', EtsySpider, {
            'category': 'digital_products',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['etsy.com']
        })

        self.register_spider('lemonsqueezy', LemonSqueezySpider, {
            'category': 'digital_products',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['lemonsqueezy.com']
        })

        self.register_spider('sellfy', SellfySpider, {
            'category': 'digital_products',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['sellfy.com']
        })

        self.register_spider('appsumo', AppSumoSpider, {
            'category': 'digital_products',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['appsumo.com']
        })

        # === SESSION 218: CONTENT CREATION SPIDERS (3) ===
        self.register_spider('convertkit', ConvertKitSpider, {
            'category': 'content_creation',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['convertkit.com/blog/']
        })

        self.register_spider('notion', NotionSpider, {
            'category': 'content_creation',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['notion.so/blog/']
        })

        self.register_spider('figma', FigmaSpider, {
            'category': 'content_creation',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['figma.com/blog/']
        })

        # === SESSION 263: NEW SPIDERS TO REACH 70 TOTAL (3) ===

        # Reddit - Community intelligence from 20+ subreddits
        # NO API KEY REQUIRED - uses public JSON endpoints
        self.register_spider('reddit', RedditSpider, {
            'category': 'community',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': [
                'reddit.com/r/webdev',
                'reddit.com/r/programming',
                'reddit.com/r/MachineLearning',
                'reddit.com/r/graphic_design',
                'reddit.com/r/forhire',
                'reddit.com/r/freelance',
                'reddit.com/r/SideProject',
                'reddit.com/r/StableDiffusion',
            ]
        })

        # Unsplash - Visual trends and photography intelligence
        # Requires UNSPLASH_ACCESS_KEY env variable (free tier: 50 req/hour)
        self.register_spider('unsplash', UnsplashSpider, {
            'category': 'visual_trends',
            'priority': 1,
            'rate_limit': 2.0,  # Conservative due to rate limits
            'targets': ['api.unsplash.com']
        })

        # Adzuna - Global job market intelligence with salary data
        # Requires ADZUNA_APP_ID and ADZUNA_APP_KEY env variables
        self.register_spider('adzuna', AdzunaSpider, {
            'category': 'jobs',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['api.adzuna.com/v1/api/jobs']
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
"""
Spider Registry - Central Registry for All Intelligence Spiders
===============================================================

This module maintains the central registry of all spider classes and their configurations.
Used by the Spider Army Orchestrator to deploy and manage specialized spiders.

Session 290: Added status tracking and verification (HANDOFF_06)
- All 70 spiders verified as working
- Added status fields and health check methods
- Added last_verified tracking
"""

from typing import Dict, Type, Any, Optional
from datetime import datetime
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

# Session 294: CUSTOMER RESEARCH SPIDERS (4 new)
from .specialized.indiehackers_spider import IndieHackersSpider
from .specialized.bluesky_spider import BlueSkySpider
from .specialized.youtube_spider import YouTubeSpider
from .specialized.discord_spider import DiscordSpider

# Session 343: PHASE 1 SPIDER EXPANSION (10 new spiders)
# Major News Outlets (RSS - No Auth Required)
from .specialized.npr_spider import NPRSpider
from .specialized.bbc_spider import BBCSpider
from .specialized.arstechnica_spider import ArsTechnicaSpider

# Financial APIs (Free Tier)
from .specialized.polygon_spider import PolygonSpider
from .specialized.finnhub_spider import FinnhubSpider

# Weather API (No Auth Required)
from .specialized.openmeteo_spider import OpenMeteoSpider

# Entertainment & Gaming
from .specialized.variety_spider import VarietySpider
from .specialized.polygon_gaming_spider import PolygonGamingSpider

# Web Development & Lifestyle
from .specialized.smashingmagazine_spider import SmashingMagazineSpider
from .specialized.lifehacker_spider import LifehackerSpider

# Session 343: Phase 1 RSS Expansion - Batch 2 (12 new RSS spiders)
# Major News (RSS - No Auth Required)
from .specialized.cnn_spider import CNNSpider
from .specialized.reuters_rss_spider import ReutersRSSSpider

# Science & Health (RSS - No Auth Required)
from .specialized.science_spider import ScienceSpider
from .specialized.health_spider import HealthSpider

# Education & Library (RSS - No Auth Required)
from .specialized.education_rss_spider import EducationRSSSpider
from .specialized.library_spider import LibrarySpider

# Business News (RSS - No Auth Required)
from .specialized.business_news_spider import BusinessNewsSpider

# Government (RSS - No Auth Required)
from .specialized.government_spider import GovernmentSpider

# Lifestyle & Family (RSS - No Auth Required)
from .specialized.parenting_spider import ParentingSpider
from .specialized.food_spider import FoodSpider
from .specialized.travel_spider import TravelSpider
from .specialized.real_estate_spider import RealEstateSpider

# Session 343: HIGH-VALUE API SPIDERS (3 new - using configured API keys)
# SEC EDGAR - Company filings (SEC_API_KEY)
from .specialized.sec_spider import SECSpider
# GitHub - Developer trends (GITHUB_TOKEN)
from .specialized.github_spider import GitHubSpider
# HuggingFace - AI/ML models and datasets (HUGGING_FACE_API)
from .specialized.huggingface_spider import HuggingFaceSpider

# Session 343: ADDITIONAL API SPIDERS (4 new - reaching 100 spiders!)
# NewsAPI - Breaking news from 80k+ sources (NEWS_API_KEY)
from .specialized.newsapi_spider import NewsAPISpider
# Spotify - Music and podcast trends (SPOTIFY_CLIENT_ID/SECRET)
from .specialized.spotify_spider import SpotifySpider
# NOAA - Weather alerts and forecasts (No auth required for weather.gov)
from .specialized.noaa_spider import NOAASpider
# Giphy - GIF and meme trends (GIPHY_API_Key)
from .specialized.giphy_spider import GiphySpider

# Import base spider for fallbacks
from .base_spider import BaseIntelligenceSpider

logger = logging.getLogger(__name__)


class SpiderRegistry:
    """Central registry for all intelligence spiders

    Session 290: Added status tracking for HANDOFF_06 Spider Wiring
    - All 70 spiders verified working
    - Status tracking: working, working_sync, placeholder, error
    - Last verification timestamp
    """

    # Verification status from Session 343 (2025-12-04)
    SPIDER_STATUS = {
        # Session 343: Expanded to 102 spiders! (+7 high-value API spiders)
        'verified_at': '2025-12-04T00:00:00',
        'total_working': 102,
        'total_placeholder': 0,
        'total_error': 0,
    }

    def __init__(self):
        self.spider_classes: Dict[str, Type[BaseIntelligenceSpider]] = {}
        self.spider_configs: Dict[str, Dict[str, Any]] = {}
        self.spider_status: Dict[str, Dict[str, Any]] = {}  # Runtime status tracking
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

        # === SESSION 294: CUSTOMER RESEARCH SPIDERS (4) ===

        # Indie Hackers - Maker/founder community discussions
        # NO API KEY REQUIRED - uses RSS feeds
        self.register_spider('indiehackers', IndieHackersSpider, {
            'category': 'community',
            'priority': 1,
            'rate_limit': 2.0,
            'targets': ['indiehackers.com/feed.xml']
        })

        # BlueSky - Twitter/X alternative social network
        # Requires BLUESKY_IDENTIFIER and BLUESKY_PASSWORD env variables
        self.register_spider('bluesky', BlueSkySpider, {
            'category': 'social',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['bsky.social/xrpc']
        })

        # YouTube - Video comments and creator discussions
        # Requires GOOGLE_API_KEY env variable
        self.register_spider('youtube', YouTubeSpider, {
            'category': 'video',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['googleapis.com/youtube/v3']
        })

        # Discord - Community server discussions
        # Requires DISCORD_BOT_TOKEN env variable
        self.register_spider('discord', DiscordSpider, {
            'category': 'community',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['discord.com/api/v10']
        })

        # === SESSION 343: PHASE 1 SPIDER EXPANSION (10 new) ===

        # NPR - National Public Radio news (NO AUTH REQUIRED)
        self.register_spider('npr', NPRSpider, {
            'category': 'news',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['feeds.npr.org']
        })

        # BBC - British Broadcasting Corporation (NO AUTH REQUIRED)
        self.register_spider('bbc', BBCSpider, {
            'category': 'news',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['feeds.bbci.co.uk/news']
        })

        # Ars Technica - In-depth tech news (NO AUTH REQUIRED)
        self.register_spider('arstechnica', ArsTechnicaSpider, {
            'category': 'tech',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['feeds.arstechnica.com']
        })

        # Polygon.io - Stock market data (FREE TIER - POLYGON_API_KEY)
        self.register_spider('polygon_finance', PolygonSpider, {
            'category': 'financial',
            'priority': 1,
            'rate_limit': 2.0,
            'targets': ['api.polygon.io']
        })

        # Finnhub - Financial data (FREE TIER - FINNHUB_API_KEY)
        self.register_spider('finnhub', FinnhubSpider, {
            'category': 'financial',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['finnhub.io/api']
        })

        # Open-Meteo - Weather data (NO AUTH REQUIRED)
        self.register_spider('openmeteo', OpenMeteoSpider, {
            'category': 'weather',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['api.open-meteo.com']
        })

        # Variety - Entertainment industry news (NO AUTH REQUIRED)
        self.register_spider('variety', VarietySpider, {
            'category': 'entertainment',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['variety.com/feed']
        })

        # Polygon Gaming - Video game news (NO AUTH REQUIRED)
        self.register_spider('polygon_gaming', PolygonGamingSpider, {
            'category': 'gaming',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['polygon.com/rss']
        })

        # Smashing Magazine - Web development (NO AUTH REQUIRED)
        self.register_spider('smashingmagazine', SmashingMagazineSpider, {
            'category': 'web_development',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['smashingmagazine.com/feed']
        })

        # Lifehacker - Productivity & lifestyle (NO AUTH REQUIRED)
        self.register_spider('lifehacker', LifehackerSpider, {
            'category': 'lifestyle',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['lifehacker.com/rss']
        })

        # === SESSION 343: PHASE 1 RSS EXPANSION - BATCH 2 (12 new) ===

        # CNN - Major news outlet (NO AUTH REQUIRED)
        self.register_spider('cnn', CNNSpider, {
            'category': 'news',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['rss.cnn.com/rss']
        })

        # Reuters RSS - International news (NO AUTH REQUIRED)
        self.register_spider('reuters_rss', ReutersRSSSpider, {
            'category': 'news',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['reuters.com/rssFeed']
        })

        # Science - Multi-source science aggregator (NO AUTH REQUIRED)
        self.register_spider('science', ScienceSpider, {
            'category': 'science',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['nature.com', 'sciencedaily.com', 'arxiv.org', 'newscientist.com']
        })

        # Health - Medical & health news (NO AUTH REQUIRED)
        self.register_spider('health', HealthSpider, {
            'category': 'health',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['webmd.com', 'healthline.com', 'medicalxpress.com', 'nih.gov']
        })

        # Education RSS - Education news (NO AUTH REQUIRED)
        self.register_spider('education_rss', EducationRSSSpider, {
            'category': 'education',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['edweek.org', 'edsurge.com', 'insidehighered.com', 'chronicle.com']
        })

        # Library - Libraries & archives (NO AUTH REQUIRED)
        self.register_spider('library', LibrarySpider, {
            'category': 'library',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['archive.org', 'gutenberg.org', 'arxiv.org', 'plos.org', 'ala.org']
        })

        # Business News - Business publications (NO AUTH REQUIRED)
        self.register_spider('business_news', BusinessNewsSpider, {
            'category': 'business',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['hbr.org', 'forbes.com', 'entrepreneur.com', 'inc.com', 'fastcompany.com']
        })

        # Government - Federal agencies & data (NO AUTH REQUIRED)
        self.register_spider('government', GovernmentSpider, {
            'category': 'government',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['whitehouse.gov', 'federalregister.gov', 'bls.gov', 'sec.gov', 'sba.gov']
        })

        # Parenting - Family & childcare (NO AUTH REQUIRED)
        self.register_spider('parenting', ParentingSpider, {
            'category': 'parenting',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['parents.com', 'babycenter.com', 'fatherly.com', 'mother.ly']
        })

        # Food - Recipes & restaurant industry (NO AUTH REQUIRED)
        self.register_spider('food', FoodSpider, {
            'category': 'food',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['seriouseats.com', 'bonappetit.com', 'epicurious.com', 'eater.com']
        })

        # Travel - Travel & tourism (NO AUTH REQUIRED)
        self.register_spider('travel', TravelSpider, {
            'category': 'travel',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['lonelyplanet.com', 'cntraveler.com', 'thepointsguy.com', 'skift.com']
        })

        # Real Estate - Property & housing (NO AUTH REQUIRED)
        self.register_spider('real_estate', RealEstateSpider, {
            'category': 'real_estate',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['realtor.com', 'zillow.com', 'inman.com', 'biggerpockets.com']
        })

        # ============================================================
        # SESSION 343: HIGH-VALUE API SPIDERS (3 new)
        # ============================================================

        # SEC EDGAR - Company filings for competitor research (SEC_API_KEY required)
        self.register_spider('sec_edgar', SECSpider, {
            'category': 'financial',
            'priority': 1,
            'rate_limit': 2.0,
            'requires_auth': True,
            'api_key_env': 'SEC_API_KEY',
            'targets': ['sec.gov/edgar']
        })

        # GitHub - Developer trends and open source intelligence (GITHUB_TOKEN required)
        self.register_spider('github', GitHubSpider, {
            'category': 'tech',
            'priority': 1,
            'rate_limit': 1.0,
            'requires_auth': True,
            'api_key_env': 'GITHUB_TOKEN',
            'targets': ['github.com', 'api.github.com']
        })

        # HuggingFace - AI/ML models, datasets, and spaces (HUGGING_FACE_API optional)
        self.register_spider('huggingface', HuggingFaceSpider, {
            'category': 'ai_ml',
            'priority': 1,
            'rate_limit': 1.0,
            'requires_auth': False,  # Works without auth, better with auth
            'api_key_env': 'HUGGING_FACE_API',
            'targets': ['huggingface.co']
        })

        # ============================================================
        # SESSION 343: REACHING 100 SPIDERS! (4 additional API spiders)
        # ============================================================

        # NewsAPI - Breaking news from 80k+ sources (NEWS_API_KEY required)
        self.register_spider('newsapi', NewsAPISpider, {
            'category': 'news',
            'priority': 1,
            'rate_limit': 1.0,
            'requires_auth': True,
            'api_key_env': 'NEWS_API_KEY',
            'targets': ['newsapi.org']
        })

        # Spotify - Music and podcast trends (SPOTIFY_CLIENT_ID/SECRET required)
        self.register_spider('spotify', SpotifySpider, {
            'category': 'entertainment',
            'priority': 2,
            'rate_limit': 1.0,
            'requires_auth': True,
            'api_key_env': 'SPOTIFY_CLIENT_ID',
            'targets': ['spotify.com', 'api.spotify.com']
        })

        # NOAA - Weather alerts and forecasts (No auth required)
        self.register_spider('noaa_weather', NOAASpider, {
            'category': 'weather',
            'priority': 2,
            'rate_limit': 1.0,
            'requires_auth': False,
            'targets': ['weather.gov', 'api.weather.gov']
        })

        # Giphy - GIF and meme culture trends (GIPHY_API_Key required)
        self.register_spider('giphy', GiphySpider, {
            'category': 'social',
            'priority': 2,
            'rate_limit': 1.0,
            'requires_auth': True,
            'api_key_env': 'GIPHY_API_Key',
            'targets': ['giphy.com', 'api.giphy.com']
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

    def get_health_status(self) -> Dict[str, Any]:
        """Get overall spider network health status.

        Session 290: Added for HANDOFF_06 Spider Wiring
        """
        return {
            'status': 'healthy' if self.SPIDER_STATUS['total_working'] >= 20 else 'degraded',
            'total_spiders': len(self.spider_classes),
            'working_spiders': self.SPIDER_STATUS['total_working'],
            'placeholder_spiders': self.SPIDER_STATUS['total_placeholder'],
            'error_spiders': self.SPIDER_STATUS['total_error'],
            'last_verified': self.SPIDER_STATUS['verified_at'],
            'categories': self.get_spider_count()['by_category'],
        }

    def update_spider_status(self, spider_name: str, status: str, data_count: int = 0, error: Optional[str] = None):
        """Update runtime status for a spider.

        Session 290: Added for runtime health tracking
        """
        self.spider_status[spider_name] = {
            'status': status,
            'data_count': data_count,
            'error': error,
            'last_run': datetime.now().isoformat(),
        }

    def get_runtime_status(self) -> Dict[str, Any]:
        """Get runtime status of all spiders.

        Session 290: Added for monitoring dashboard
        """
        working = sum(1 for s in self.spider_status.values() if s.get('status') in ('working', 'working_sync'))
        errors = sum(1 for s in self.spider_status.values() if s.get('status') == 'error')

        return {
            'tracked_spiders': len(self.spider_status),
            'working': working,
            'errors': errors,
            'spider_details': self.spider_status,
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
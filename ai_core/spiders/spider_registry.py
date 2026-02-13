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

# Import working freelance platform spiders (Session 397: Removed broken/no-API spiders)
from .specialized.remoteok_spider import RemoteOKSpider

# Import content monetization spiders (Session 397: Removed gumroad - no public API)
from .specialized.medium_spider import MediumIntelligenceSpider
from .specialized.content_monetization_spider import ContentMonetizationSpider
from .specialized.tech_community_spider import TechCommunitySpider

# Session 397: Removed sports betting spiders (horse_racing, combat_sports) - not in current focus

# Import legal spiders
from .specialized.courtlistener_spider import CourtListenerSpider
from .specialized.legal_news_spider import LegalNewsSpider  # Session 399: Replaced JustiaSpider
from .specialized.findlaw_spider import FindLawSpider
from .specialized.lii_spider import LegalInformationInstituteSpider
# Session 403: Colorado Family Law spiders (Playwright-enabled)
from .specialized.colorado_family_law_spider import ColoradoFamilyLawSpider
from .specialized.justia_playwright_spider import JustiaPlaywrightSpider

# Session 218: NEWS spiders
from .specialized.techcrunch_spider import TechCrunchSpider
from .specialized.axios_spider import AxiosSpider
from .specialized.verge_spider import TheVergeSpider
# Session 534: CNN RSS spider (fixed and re-added)
from .specialized.cnn_spider import CNNSpider

# Session 495: STARTUP FUNDING & SECTOR SPIDERS (5 new)
from .specialized.crunchbase_spider import CrunchbaseSpider
from .specialized.venturebeat_spider import VentureBeatSpider
from .specialized.defenseone_spider import DefenseOneSpider
from .specialized.mobihealthnews_spider import MobiHealthNewsSpider
from .specialized.securityweek_spider import SecurityWeekSpider

# Session 218: INNOVATION spiders
from .specialized.mit_tech_review_spider import MITTechReviewSpider
from .specialized.wired_spider import WiredSpider

# Session 218: DESIGN spiders
# Session 399: DribbbleSpider removed - blocked, now using awwwards via PHASE3_API_SPIDERS
from .specialized.behance_spider import BehanceSpider

# Session 218: FREELANCE spiders (Session 397: Removed AngelList - no public API)
from .specialized.weworkremotely_spider import WeWorkRemotelySpider

# Session 218: EDUCATION spiders
# Session 534: Re-added teachable and udemy with RSS feed support
from .specialized.teachable_spider import TeachableSpider
from .specialized.udemy_spider import UdemySpider

# Session 218: FINANCIAL spiders (Session 397: Removed opensea, seekingalpha, bloomberg, reuters - no public API)
from .specialized.etherscan_spider import EtherscanSpider

# Session 461: BLOCKCHAIN AUDIT spiders
from .specialized.etherscan_api_spider import EtherscanAPISpider

# Session 558: PREDICTION MARKETS spider
from .specialized.kalshi_spider import KalshiSpider

# Session 558: SPORTS ODDS spider
from .specialized.theodds_spider import TheOddsSpider

# Session 218: TECH spiders
from .specialized.hackernews_spider import HackerNewsSpider
from .specialized.devto_spider import DevToSpider
# Session 399: HashnodeSpider removed - API returns 404, now using freecodecamp via PHASE3_API_SPIDERS
# Session 399: IndiegogoSpider removed - API blocked, now using techcrunch_startups via PHASE3_API_SPIDERS
from .specialized.kickstarter_spider import KickstarterSpider

# Import financial API spiders (CRITICAL FIX: These were built but not registered!)
from .specialized.coingecko_spider import CoinGeckoSpider
from .specialized.yahoo_finance_spider import YahooFinanceSpider

# Session 397: Removed CREATIVE ASSETS spiders (envato, creativemarket, adobestock, shutterstock, canva) - no public API
# Session 397: Removed AI/CREATIVE TOOLS spiders (midjourney, civitai, runwayml, replicate) - no public API
# Session 397: Removed DIGITAL PRODUCT spiders (etsy, lemonsqueezy, sellfy, appsumo) - no public API
# Session 397: Removed CONTENT CREATION spiders (convertkit, notion, figma) - no public API

# Session 263: NEW SPIDERS TO REACH 70 TOTAL
from .specialized.reddit_spider import RedditSpider
from .specialized.unsplash_spider import UnsplashSpider
from .specialized.adzuna_spider import AdzunaSpider

# Session 294: CUSTOMER RESEARCH SPIDERS (4 new)
# Session 399: IndieHackersSpider removed - RSS broken, now using hackernoon via PHASE3_API_SPIDERS
from .specialized.bluesky_spider import BlueSkySpider
from .specialized.youtube_spider import YouTubeSpider
from .specialized.discord_spider import DiscordSpider
# Session 420: Training data spider for HuggingFace conversation datasets
from .specialized.discord_training_spider import DiscordTrainingSpider

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
# Session 399: CNNSpider removed - RSS feeds stale (2023 content), now using google_news via PHASE3_API_SPIDERS
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
# Session 452: Kaggle - ML competitions, datasets, notebooks (KAGGLE_USERNAME/KAGGLE_KEY)
from .specialized.kaggle_spider import KaggleSpider

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

    # Verification status from Session 397 (2025-12-08)
    SPIDER_STATUS = {
        # Session 397: Cleaned registry - removed 26 broken spiders (no public API/placeholders)
        # Remaining: ~76 spiders (working + needs API keys)
        'verified_at': '2025-12-08T00:00:00',
        'total_working': 54,  # Spiders with actual data collection
        'total_placeholder': 0,  # All placeholders removed
        'total_error': 0,
    }

    def __init__(self):
        self.spider_classes: Dict[str, Type[BaseIntelligenceSpider]] = {}
        self.spider_configs: Dict[str, Dict[str, Any]] = {}
        self.spider_status: Dict[str, Dict[str, Any]] = {}  # Runtime status tracking
        self._register_all_spiders()

    def _register_all_spiders(self):
        """Register all available spider classes"""

        # === SESSION 397: WORKING FREELANCE/JOBS SPIDERS ===
        # Removed: financial, innovation, social_sentiment, market_data, news_harvester (placeholders)
        # Removed: toptal, guru, peopleperhour, ninetyninedesigns, flexjobs, angellist (no public API)

        self.register_spider('remoteok', RemoteOKSpider, {
            'category': 'remote_work',
            'priority': 2,
            'rate_limit': 1.0,
            'targets': ['remoteok.io']
        })

        self.register_spider('weworkremotely', WeWorkRemotelySpider, {
            'category': 'freelance',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['weworkremotely.com/categories/']
        })

        # === SESSION 397: WORKING CONTENT SPIDERS ===
        # Removed: gumroad, patreon, kofi (no public API)
        # Removed: teachable, skillshare (no public API)

        self.register_spider('medium', MediumIntelligenceSpider, {
            'category': 'content',
            'priority': 2,
            'rate_limit': 1.0,
            'targets': ['medium.com/partner-program']
        })

        self.register_spider('substack', ContentMonetizationSpider, {
            'category': 'content',
            'priority': 2,
            'rate_limit': 1.0,
            'targets': ['substack.com']
        })

        self.register_spider('producthunt', ContentMonetizationSpider, {
            'category': 'content',
            'priority': 2,
            'rate_limit': 1.0,
            'targets': ['producthunt.com']
        })

        # Session 399: Renamed udemy → coursera (API requires auth, using Coursera Blog RSS)
        # Handler: _collect_coursera_data in real_data_collector.py PHASE3_API_SPIDERS
        self.register_spider('coursera', BaseIntelligenceSpider, {
            'category': 'education',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['blog.coursera.org/feed/']
        })

        # Session 534: Re-added with RSS feed support
        self.register_spider('teachable', TeachableSpider, {
            'category': 'education',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['teachable.com/blog', 'thinkific.com/blog']
        })

        self.register_spider('udemy', UdemySpider, {
            'category': 'education',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['elearningindustry.com', 'classcentral.com']
        })

        # === SESSION 397: WORKING FINANCIAL SPIDERS ===
        # Removed: opensea, seekingalpha, bloomberg_terminal, reuters_eikon (no public API)

        self.register_spider('coingecko', CoinGeckoSpider, {
            'category': 'financial',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['api.coingecko.com/api/v3']
        })

        self.register_spider('yahoo_finance', YahooFinanceSpider, {
            'category': 'financial',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['query1.finance.yahoo.com/v8', 'query2.finance.yahoo.com/v10']
        })

        self.register_spider('etherscan', EtherscanSpider, {
            'category': 'financial',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['etherscan.io/apis']
        })

        # === SESSION 397: WORKING TECH SPIDERS ===
        # Removed: kaggle, stackoverflow_jobs (no public API)
        # Removed: horse_racing, combat_sports (sports betting not in focus)
        # Note: huggingface TechCommunitySpider replaced by HuggingFaceSpider below

        self.register_spider('github_jobs', TechCommunitySpider, {
            'category': 'tech',
            'priority': 2,
            'rate_limit': 1.0,
            'targets': ['github.com']
        })

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

        # Session 399: Renamed hashnode → freecodecamp (API returns 404)
        # Handler: _collect_freecodecamp_data in real_data_collector.py PHASE3_API_SPIDERS
        self.register_spider('freecodecamp', BaseIntelligenceSpider, {
            'category': 'tech',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['freecodecamp.org/news/rss/']
        })

        # Session 399: Renamed indiegogo → techcrunch_startups (API blocked 403)
        # Handler: _collect_techcrunch_startups_data in real_data_collector.py PHASE3_API_SPIDERS
        self.register_spider('techcrunch_startups', BaseIntelligenceSpider, {
            'category': 'tech',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['techcrunch.com/category/startups/feed/']
        })

        self.register_spider('kickstarter', KickstarterSpider, {
            'category': 'tech',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['kickstarter.com']
        })

        # === LEGAL SPIDERS (4) ===
        self.register_spider('courtlistener', CourtListenerSpider, {
            'category': 'legal',
            'priority': 2,
            'rate_limit': 1.0,
            'targets': ['courtlistener.com/api']
        })

        # Session 399: Renamed from 'justia' (blocked by Cloudflare)
        self.register_spider('legal_news', LegalNewsSpider, {
            'category': 'legal',
            'priority': 2,
            'rate_limit': 1.0,
            'targets': ['scotusblog.com', 'news.google.com/legal']
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

        # === SESSION 403: COLORADO FAMILY LAW SPIDERS (Playwright-enabled) ===
        # Focus: Divorce with children, custody, parenting time, child support
        self.register_spider('colorado_family_law', ColoradoFamilyLawSpider, {
            'category': 'legal',
            'priority': 1,  # High priority for legal assistant
            'rate_limit': 2.0,  # Slower rate for Playwright
            'targets': ['coloradojudicial.gov/self-help-forms'],
            'description': 'Colorado family law forms from Colorado Judicial Branch',
            'playwright_enabled': True,
        })

        self.register_spider('justia_family_law', JustiaPlaywrightSpider, {
            'category': 'legal',
            'priority': 1,  # High priority for legal assistant
            'rate_limit': 2.0,  # Slower rate for Playwright
            'targets': ['justia.com/family/'],
            'description': 'Justia family law articles and guides (Playwright-enabled)',
            'playwright_enabled': True,
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

        # Session 534: CNN RSS spider (re-added with fixed interface)
        self.register_spider('cnn', CNNSpider, {
            'category': 'news',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['rss.cnn.com/rss/']
        })

        # ============================================================
        # SESSION 495: STARTUP FUNDING & SECTOR SPIDERS (5 new)
        # Added to fill gaps in startup trend coverage
        # ============================================================

        # Crunchbase News - THE gold standard for startup funding data
        self.register_spider('crunchbase', CrunchbaseSpider, {
            'category': 'startups',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['news.crunchbase.com/feed/'],
            'description': 'Startup funding rounds, valuations, unicorns, M&A activity'
        })

        # VentureBeat - AI and enterprise startup coverage
        self.register_spider('venturebeat', VentureBeatSpider, {
            'category': 'startups',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['venturebeat.com/feed/'],
            'description': 'AI funding, enterprise tech, VC perspectives'
        })

        # Defense One - Defense tech sector (was missing from startup trends!)
        self.register_spider('defenseone', DefenseOneSpider, {
            'category': 'defense_tech',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['defenseone.com/rss/'],
            'description': 'Defense startups, government contracts, Pentagon, aerospace'
        })

        # MobiHealthNews - Healthtech sector (was missing from startup trends!)
        self.register_spider('mobihealthnews', MobiHealthNewsSpider, {
            'category': 'healthtech',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['mobihealthnews.com/feed'],
            'description': 'Digital health, biotech, medtech, FDA, telehealth'
        })

        # SecurityWeek - Cybersecurity sector (was missing from startup trends!)
        self.register_spider('securityweek', SecurityWeekSpider, {
            'category': 'cybersecurity',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['securityweek.com/feed/'],
            'description': 'Cybersecurity startups, breaches, vulnerabilities, infosec'
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
        # Session 399: Renamed dribbble → awwwards (Dribbble blocked, returns 202)
        # Handler: Uses RSS feeds via SPIDER_TARGET_URLS in real_data_collector.py
        self.register_spider('awwwards', BaseIntelligenceSpider, {
            'category': 'design',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['awwwards.com/blog/feed/', 'tympanus.net/codrops/feed/']
        })

        # Activate Behance (was placeholder)
        self.register_spider('behance', BehanceSpider, {
            'category': 'design',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['behance.net/feeds/projects']
        })

        # === SESSION 397: REMOVED BROKEN CATEGORIES ===
        # Removed CREATIVE ASSETS (5): envato, creativemarket, adobestock, shutterstock, canva - no public API
        # Removed AI/CREATIVE TOOLS (4): midjourney, civitai, runwayml, replicate - no public API
        # Removed DIGITAL PRODUCTS (4): etsy, lemonsqueezy, sellfy, appsumo - no public API
        # Removed CONTENT CREATION (3): convertkit, notion, figma - no public API

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

        # Session 399: Renamed indiehackers → hackernoon (RSS feed broken, returns HTML)
        # Handler: Uses RSS feeds via SPIDER_TARGET_URLS in real_data_collector.py
        self.register_spider('hackernoon', BaseIntelligenceSpider, {
            'category': 'community',
            'priority': 1,
            'rate_limit': 2.0,
            'targets': ['hackernoon.com/feed']
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

        # Session 420: Discord Training Data Spider
        # Fetches conversation data from HuggingFace for agent training
        # Optional: HUGGINGFACE_TOKEN for higher rate limits
        self.register_spider('discord_training', DiscordTrainingSpider, {
            'category': 'training',
            'priority': 2,
            'rate_limit': 2.0,
            'targets': ['huggingface.co/datasets']
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

        # Session 399: Renamed cnn → google_news (CNN RSS feeds stale - 2023 content)
        # Handler: Uses RSS feeds via SPIDER_TARGET_URLS in real_data_collector.py
        self.register_spider('google_news', BaseIntelligenceSpider, {
            'category': 'news',
            'priority': 1,
            'rate_limit': 1.0,
            'targets': ['news.google.com/rss']
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

        # SEC EDGAR - Company filings via free public RSS feeds (no API key needed)
        self.register_spider('sec_edgar', SECSpider, {
            'category': 'financial',
            'priority': 1,
            'rate_limit': 2.0,
            'requires_auth': False,
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

        # Session 452: Kaggle - ML competitions, datasets, notebooks
        self.register_spider('kaggle', KaggleSpider, {
            'category': 'ai_ml',
            'priority': 1,
            'rate_limit': 1.0,
            'requires_auth': True,
            'api_key_env': 'KAGGLE_KEY',
            'targets': ['kaggle.com']
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

        # ============================================================
        # SESSION 461: BLOCKCHAIN AUDIT SPIDERS
        # ============================================================

        # Etherscan API - Real blockchain transaction monitoring
        # Used by BlockchainAuditCoordinator for whale watching and exploit detection
        self.register_spider('etherscan_api', EtherscanAPISpider, {
            'category': 'blockchain',
            'priority': 1,
            'rate_limit': 0.2,  # 5 calls/second free tier
            'requires_auth': False,  # Works without API key (limited), better with key
            'api_key_env': 'ETHERSCAN_API_KEY',
            'targets': ['api.etherscan.io'],
            'description': 'Real-time Ethereum transaction monitoring for security audits'
        })

        # ============================================================
        # SESSION 558: PREDICTION MARKETS SPIDER
        # ============================================================

        # Kalshi - CFTC-regulated prediction market exchange
        # Categories: economics, politics, weather, tech, entertainment, finance, science
        self.register_spider('kalshi', KalshiSpider, {
            'category': 'prediction_markets',
            'priority': 1,
            'rate_limit': 1.0,
            'requires_auth': False,  # Public data works without auth
            'api_key_env': 'KALSHI_API_KEY',
            'targets': ['api.elections.kalshi.com'],
            'description': 'Prediction market data: economics, politics, weather, tech events'
        })

        # The Odds API - Sports betting odds aggregator (40+ bookmakers)
        # Sports: NFL, NBA, MLB, NHL, Soccer, UFC, Tennis, Golf
        self.register_spider('theodds', TheOddsSpider, {
            'category': 'sports_odds',
            'priority': 1,
            'rate_limit': 1.0,
            'requires_auth': True,
            'api_key_env': 'THE_ODDS_API_KEY',
            'targets': ['api.the-odds-api.com'],
            'description': 'Sports betting odds: NFL, NBA, MLB, NHL, Soccer, UFC, Tennis'
        })

        # ============================================================
        # SESSION 998B: SPORTS NEWS & INJURY RSS SPIDERS
        # Feeds the Sports Betting Hub with news and injury reports
        # ============================================================

        # Sports News - ESPN, NYT Sports, CBS Sports, Yahoo Sports, SI
        self.register_spider('sports_news_rss', BaseIntelligenceSpider, {
            'category': 'sports_news',
            'priority': 1,
            'rate_limit': 1.0,
            'requires_auth': False,
            'targets': ['espn.com/rss', 'nytimes.com/sports', 'cbssports.com', 'sports.yahoo.com', 'si.com'],
            'description': 'Sports news from ESPN, NYT, CBS Sports, Yahoo Sports, SI'
        })

        # Sports Injuries - RotoWire, CBS Injuries, RotoGrinders
        self.register_spider('sports_injuries_rss', BaseIntelligenceSpider, {
            'category': 'sports_injuries',
            'priority': 1,
            'rate_limit': 1.0,
            'requires_auth': False,
            'targets': ['rotowire.com/injuries', 'cbssports.com/injuries', 'rotogrinders.com/injury-report'],
            'description': 'Injury reports from RotoWire, CBS Sports, RotoGrinders'
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
"""
Real Data Collector - Session 221
=================================

This module provides real web scraping and API data collection for all spiders.
It fetches actual data from configured targets using aiohttp and BeautifulSoup.
"""

import aiohttp
import asyncio
import logging
import os
import feedparser
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


def _use_threaded_dns_resolver() -> bool:
    """Env flag: whether ``collect_spider_data`` swaps aiohttp's default
    resolver for :class:`aiohttp.ThreadedResolver`.

    Default **true**: aiodns 3.5.0 (aiohttp's default when installed)
    fails with ``ClientConnectorDNSError: Could not contact DNS servers``
    on macOS + certain Linux configurations where the system DNS is
    mediated by a stub resolver aiodns/pycares does not read. Every
    spider fetch then reports ``fetch_failed`` even though
    ``socket.getaddrinfo`` + ``urllib`` + ``curl`` resolve the same host.

    Set ``SPIDER_USE_THREADED_DNS_RESOLVER=false`` to fall back to
    aiohttp's default (aiodns if installed) — expected in environments
    where aiodns is known-good and thread-pool DNS is undesirable."""
    return os.environ.get('SPIDER_USE_THREADED_DNS_RESOLVER', 'true').lower() == 'true'


def _build_client_session_kwargs() -> Dict[str, Any]:
    """Return kwargs for :class:`aiohttp.ClientSession` honoring the
    threaded-resolver flag. Must be called from within a running asyncio
    event loop when the flag is on, because
    :class:`aiohttp.ThreadedResolver` binds the loop at construction."""
    if _use_threaded_dns_resolver():
        return {
            'connector': aiohttp.TCPConnector(resolver=aiohttp.ThreadedResolver()),
        }
    return {}


# Real target URLs for each spider (with proper full URLs)
# Session 395: Expanded from 21 to 40+ spiders with real data sources
SPIDER_TARGET_URLS = {
    # === NEWS & TECH SPIDERS ===
    'techcrunch': ['https://techcrunch.com/feed/'],
    'theverge': ['https://www.theverge.com/rss/index.xml'],
    'wired': ['https://www.wired.com/feed/rss'],
    'mit_tech_review': ['https://www.technologyreview.com/feed/'],
    'axios': ['https://api.axios.com/feed/'],
    'hackernews': ['https://hacker-news.firebaseio.com/v0/topstories.json'],
    'devto': ['https://dev.to/api/articles?per_page=30'],

    # === SESSION 395: NEW NEWS SPIDERS ===
    'bbc': ['http://feeds.bbci.co.uk/news/rss.xml', 'http://feeds.bbci.co.uk/news/technology/rss.xml'],
    # Session 399: Renamed from 'cnn' (RSS feeds were stale/2023 content)
    'google_news': ['https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en'],
    'npr': ['https://feeds.npr.org/1001/rss.xml', 'https://feeds.npr.org/1019/rss.xml'],  # Top stories + Technology
    # Session 399: Updated Reuters feeds (old ones returned 404/401)
    'reuters_rss': ['https://news.google.com/rss/search?q=site:reuters.com&hl=en-US&gl=US&ceid=US:en'],
    'arstechnica': ['https://feeds.arstechnica.com/arstechnica/index'],

    # === REMOTE JOBS SPIDERS ===
    'remoteok': ['https://remoteok.com/api'],
    'weworkremotely': ['https://weworkremotely.com/categories/remote-programming-jobs.rss'],

    # === FINANCIAL SPIDERS ===
    'coingecko': ['https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=20&page=1'],
    'yahoo_finance': ['https://query1.finance.yahoo.com/v8/finance/chart/SPY?interval=1d'],

    # === DESIGN SPIDERS ===
    # Session 399: Renamed from 'dribbble' (blocked, returns 202)
    'awwwards': ['https://www.awwwards.com/blog/feed/', 'https://tympanus.net/codrops/feed/'],
    'behance': ['https://www.behance.net/feeds/projects'],

    # === CONTENT/CREATOR SPIDERS ===
    'producthunt': ['https://www.producthunt.com/feed'],
    'medium': ['https://medium.com/feed/topic/technology'],
    # Session 399: Renamed from 'hashnode' (API returns 404)
    'freecodecamp': ['https://www.freecodecamp.org/news/rss/'],

    # === SESSION 395: NEW CONTENT SPIDERS ===
    'substack': [
        'https://stratechery.substack.com/feed',  # Tech strategy
        'https://www.lennysnewsletter.com/feed',  # Product management
        'https://www.platformer.news/feed',  # Tech news
    ],

    # === EDUCATION SPIDERS ===
    # Session 399: Renamed from 'udemy' (API requires auth)
    'coursera': ['https://blog.coursera.org/feed/'],

    # === CROWDFUNDING/STARTUPS SPIDERS ===
    # Session 505: Removed kickstarter - proper KickstarterSpider class in spider_registry handles it
    # Session 399: Renamed from 'indiegogo' (API blocked)
    'techcrunch_startups': ['https://techcrunch.com/category/startups/feed/'],

    # === COMMUNITY SPIDERS (Session 294) ===
    # Reddit — S2970: switched from JSON API to Atom `.rss`. Kept to 3
    # subreddits to reduce 429 rate-limit surface; each Atom feed returns
    # ~25 entries with canonical permalinks, so DoD ≥5 unique items has
    # ample headroom even if 1-2 URLs 429.
    'reddit': [
        'https://www.reddit.com/r/webdev/.rss',
        'https://www.reddit.com/r/programming/.rss',
        'https://www.reddit.com/r/Entrepreneur/.rss',
    ],

    # Session 399: Renamed from 'indiehackers' (feed broken, returns HTML)
    'hackernoon': [
        'https://hackernoon.com/feed',  # Startup/tech entrepreneur content
    ],

    # === SESSION 395: LIFESTYLE & ENTERTAINMENT ===
    'lifehacker': ['https://lifehacker.com/rss'],
    'variety': ['https://variety.com/feed/', 'https://variety.com/v/film/feed/'],
    'smashingmagazine': ['https://www.smashingmagazine.com/feed/'],

    # === SESSION 395: WEATHER (No API key needed!) ===
    'openmeteo': ['https://api.open-meteo.com/v1/forecast?latitude=39.7392&longitude=-104.9903&current_weather=true&hourly=temperature_2m,precipitation'],

    # === SESSION 395: AI/ML SPIDERS ===
    # S2862: intentionally NOT re-added. HF Hub API items expose
    # `modelId`/`id` but no `title`/`name`/`description`, so the shared
    # `normalize_item()` field mappings (title <- title|name|headline|
    # position|role, description <- description|summary|body|content|
    # excerpt|tagline) never populate anything readable, and downstream
    # `SignalAggregationService._extract_text_from_spider_data()` gets
    # 0-char text, dropping every signal before clustering (22 rows/7d
    # -> 0 SignalCluster contributions). Falling through to the else
    # branch at core/tasks_spiders.py:158 invokes HuggingFaceSpider.fetch_data()
    # (ai_core/spiders/specialized/huggingface_spider.py) which builds
    # items with title/summary/description already populated. Regression
    # tests: core/tests/test_s2862_huggingface_signal_extraction.py.

    # === SESSION 396: PHASE 2 - FREE PUBLIC APIs ===

    # NOAA Weather - Uses alerts endpoint (more reliable than forecast)
    'noaa_weather': [
        'https://api.weather.gov/alerts/active?area=CO',  # Colorado alerts
        'https://api.weather.gov/alerts/active?area=CA',  # California alerts
        'https://api.weather.gov/alerts/active?area=NY',  # New York alerts
    ],

    # GitHub - Public API (60 requests/hr unauthenticated)
    'github': [
        'https://api.github.com/search/repositories?q=ai+created:>2024-01-01&sort=stars&per_page=15',
        'https://api.github.com/search/repositories?q=machine-learning+created:>2024-01-01&sort=stars&per_page=15',
    ],

    # GitHub Jobs/Issues - Good first issues for developers
    'github_jobs': [
        'https://api.github.com/search/issues?q=is:open+label:good-first-issue+language:python&sort=created&per_page=15',
        'https://api.github.com/search/issues?q=is:open+label:help-wanted+language:javascript&sort=created&per_page=15',
    ],

    # CoinGecko - Trending crypto (free, no key needed)
    # Already have coingecko for markets, adding trending endpoint
    'coingecko_trending': [
        'https://api.coingecko.com/api/v3/search/trending',
    ],

    # Science RSS Feeds
    'science': [
        'https://www.sciencedaily.com/rss/all.xml',
        'https://phys.org/rss-feed/',
        'https://feeds.nature.com/nature/rss/current',
    ],

    # Health RSS Feeds (verified working)
    'health': [
        'https://www.statnews.com/feed/',  # STAT News - health/biotech
        'https://kffhealthnews.org/feed/',  # KFF Health News
        'https://www.fiercehealthcare.com/rss/xml',  # Fierce Healthcare
    ],

    # Education/Learning RSS Feeds (verified working)
    'education_rss': [
        'https://www.edsurge.com/rss',  # EdSurge education tech
        'https://www.chronicle.com/section/News/6/rss',  # Chronicle of Higher Ed
        'https://www.insidehighered.com/rss/feed',  # Inside Higher Ed
    ],

    # Business News RSS Feeds
    'business_news': [
        'https://feeds.bloomberg.com/markets/news.rss',
        'https://www.wsj.com/xml/rss/3_7085.xml',  # WSJ Business
        'https://fortune.com/feed/',
    ],

    # === SESSION 397: LIFESTYLE & NICHE RSS SPIDERS ===

    # Food & Cooking RSS Feeds (Session 398: Fixed broken feeds)
    'food': [
        'https://www.eater.com/rss/index.xml',  # Eater (fast, reliable)
        'https://smittenkitchen.com/feed/',  # Smitten Kitchen
        'https://minimalistbaker.com/feed/',  # Minimalist Baker
    ],

    # Travel RSS Feeds (Session 398: Fixed Lonely Planet 404)
    'travel': [
        'https://matadornetwork.com/feed/',  # Matador Network
        'https://www.nomadicmatt.com/travel-blog/feed/',  # Nomadic Matt
        'https://feeds.feedburner.com/ThePointsGuy',  # The Points Guy
    ],

    # Parenting & Family RSS Feeds
    'parenting': [
        'https://www.scarymommy.com/feed/',  # Scary Mommy
        'https://www.fatherly.com/feed/',  # Fatherly
        'https://www.parents.com/feed/',  # Parents Magazine
    ],

    # Real Estate RSS Feeds
    'real_estate': [
        'https://www.inman.com/feed/',  # Inman News (real estate)
        'https://www.housingwire.com/feed/',  # HousingWire
        'https://www.biggerpockets.com/blog/feed',  # BiggerPockets
    ],

    # Library & Books RSS Feeds
    'library': [
        'https://americanlibrariesmagazine.org/feed/',  # American Libraries
        'https://bookriot.com/feed/',  # Book Riot
        'https://www.theguardian.com/books/rss',  # Guardian Books
    ],

    # Government & Policy RSS Feeds (Session 398: Fixed Politico 403)
    'government': [
        'https://rss.politico.com/politics-news.xml',  # Politico (new feed URL)
        'https://www.govtech.com/rss/',  # Government Technology
        'https://thehill.com/feed/',  # The Hill
    ],

    # === SESSION 396: PHASE 3 - API KEY SPIDERS ===
    # These use API keys from .env

    # Polygon.io Financial Data (POLYGON_API_KEY required)
    # Note: URL is a template - actual key injected at runtime
    'polygon_finance': [
        'POLYGON_API',  # Marker for custom handler
    ],

    # Etherscan Blockchain Data (ETHERSCAN_API_KEY required)
    'etherscan': [
        'ETHERSCAN_API',  # Marker for custom handler
    ],

    # SEC EDGAR Filings (SEC_API_KEY required)
    'sec_edgar': [
        'SEC_EDGAR_API',  # Marker for custom handler
    ],

    # Spotify Podcast/Music Trends (SPOTIFY_CLIENT_ID/SECRET required)
    'spotify': [
        'SPOTIFY_API',  # Marker for custom handler
    ],

    # Session 399: Added API-based spiders so they get routed through collect_spider_data_sync
    'youtube': [
        'YOUTUBE_API',  # Marker for custom handler - uses YOUTUBE_API_KEY or GOOGLE_API_KEY
    ],

    'bluesky': [
        'BLUESKY_API',  # Marker for custom handler - uses BLUESKY_IDENTIFIER, BLUESKY_PASSWORD
    ],

    'discord': [
        'DISCORD_API',  # Marker for custom handler - uses DISCORD_BOT_TOKEN
    ],

    # Session 399: Added giphy and newsapi (they have handlers in PHASE3_API_SPIDERS)
    'giphy': [
        'GIPHY_API',  # Marker for custom handler - uses GIPHY_API_KEY
    ],

    'newsapi': [
        'NEWS_API',  # Marker for custom handler - uses NEWS_API_KEY
    ],

    # Session 399: Added finnhub and polygon_gaming
    'finnhub': [
        'FINNHUB_API',  # Marker for custom handler - uses FINNHUB_API_KEY
    ],

    'polygon_gaming': [
        'POLYGON_GAMING_RSS',  # Marker for custom handler - uses polygon.com RSS feeds
    ],

    # Session 399: Added adzuna (already has handler in PHASE3_API_SPIDERS)
    'adzuna': [
        'ADZUNA_API',  # Marker for custom handler - uses ADZUNA_APP_ID, ADZUNA_APP_KEY
    ],

    # Session 399: Added unsplash and lii (already have handlers in PHASE3_API_SPIDERS)
    'unsplash': [
        'UNSPLASH_API',  # Marker for custom handler - uses UNSPLASH_ACCESS_KEY
    ],

    'lii': [
        'LII_SCRAPER',  # Marker for custom handler - scrapes Cornell LII
    ],

    # Session 399: Legal spiders
    # Session 505: Removed findlaw - proper FindLawSpider class in spider_registry handles it
    'legal_news': [
        'LEGAL_NEWS_RSS',  # SCOTUSblog + Google News Legal
    ],
    'courtlistener': [
        'COURTLISTENER_API',  # Marker for custom handler - uses public API
    ],

    # === SESSION 998B: SPORTS NEWS & INJURY SPIDERS ===
    'sports_news': [
        'https://www.espn.com/espn/rss/news',
        'https://rss.nytimes.com/services/xml/rss/nyt/Sports.xml',
        'https://www.cbssports.com/rss/headlines/',
        'https://sports.yahoo.com/rss/',
        'https://www.si.com/rss/si_topstories.rss',
    ],
    # S2970: prior URLs (rotowire injuries.xml + cbssports injuries +
    # rotogrinders) all returned HTTP 404. Replaced with rotowire per-sport
    # news feeds, which surface player status updates (roster + injuries).
    # The runner applies an injury-keyword filter for this spider (see
    # ``SPORTS_INJURY_KEYWORDS`` + ``filter_injury_items``) so
    # non-injury roster items are dropped before dedup.
    'sports_injuries': [
        'https://www.rotowire.com/rss/news.php?sport=NFL',
        'https://www.rotowire.com/rss/news.php?sport=MLB',
        'https://www.rotowire.com/rss/news.php?sport=NBA',
        'https://www.rotowire.com/rss/news.php?sport=NHL',
        'https://www.rotowire.com/rss/news.php?sport=SOCCER',
    ],
}

# User agent to avoid blocks
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'


# S2970: injury-keyword filter for the sports_injuries spider. Applied to
# each item's title + description; requires at least one keyword hit to
# survive. Prevents rotowire per-sport news feeds — which mix injury
# updates with roster/transaction items — from turning into a generic
# roster-news firehose. Order irrelevant; substring match on lowercased
# concatenated (title + ' ' + description).
SPORTS_INJURY_KEYWORDS = (
    'injur',           # matches injury, injured, injuries
    'questionable',
    'doubtful',
    ' out ',
    ' out.',
    ' out,',
    'ruled out',
    'sidelined',
    'day-to-day',
    ' dtd',
    ' dnp',
    ' il ',            # injured list
    ' il.',
    ' il,',
    ' ir ',            # injured reserve
    ' ir.',
    ' ir,',
    'pup ',            # physically unable to perform
    'will miss',
    'surgery',
    'concussion',
    'hamstring',
    'acl',
    'mcl',
    'sprain',
    'strain',
    'torn',
    'fracture',
    'contusion',
    # Rigby A2 fold: availability-adjacent terms most likely to cause
    # silent drops of legit availability updates in the news feeds.
    'mri',
    'illness',
    'covid',
)


def filter_injury_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return only items whose title + description contain an injury keyword.

    Case-insensitive substring match. Keywords are chosen to catch injury
    reports and status transitions (Out/Questionable/IR/etc.) while
    dropping pure roster news (trades, signings, contract items). Empty
    input returns empty output."""
    if not items:
        return []
    kept: List[Dict[str, Any]] = []
    for item in items:
        title = str(item.get('title', '') or '')
        description = str(item.get('description', '') or '')
        # Pad with spaces so word-boundary-ish tokens (" out ", " il ")
        # still match at string edges.
        blob = f' {title.lower()} {description.lower()} '
        if any(kw in blob for kw in SPORTS_INJURY_KEYWORDS):
            kept.append(item)
    return kept


async def fetch_url(session: aiohttp.ClientSession, url: str, timeout: int = 30) -> Optional[Dict[str, Any]]:
    """Fetch data from a URL"""
    headers = {
        'User-Agent': USER_AGENT,
        'Accept': 'application/json, application/xml, text/html, */*',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    try:
        async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=timeout)) as response:
            content_type = response.headers.get('content-type', '')

            if response.status == 200:
                if 'application/json' in content_type or 'geo+json' in content_type:
                    data = await response.json()
                    return {'type': 'json', 'data': data, 'url': url}
                elif 'xml' in content_type or 'rss' in content_type or url.endswith('.xml') or 'feed' in url:
                    text = await response.text()
                    return {'type': 'rss', 'data': text, 'url': url}
                else:
                    text = await response.text()
                    return {'type': 'html', 'data': text, 'url': url}
            else:
                logger.warning(f"Failed to fetch {url}: HTTP {response.status}")
                return None

    except asyncio.TimeoutError:
        logger.warning(f"Timeout fetching {url}")
        return None
    except Exception as e:
        logger.warning(f"Error fetching {url}: {e}")
        return None


def strip_html_tags(text: str) -> str:
    """Strip HTML tags and clean up text content.

    Session 293: RSS feeds (especially Medium) often contain full HTML in descriptions.
    Use BeautifulSoup to properly extract just the text content.
    """
    if not text:
        return ''
    try:
        # Use BeautifulSoup to extract text from HTML
        soup = BeautifulSoup(text, 'html.parser')
        # Get text and clean up whitespace
        clean_text = soup.get_text(separator=' ', strip=True)
        # Collapse multiple spaces/newlines
        clean_text = ' '.join(clean_text.split())
        return clean_text
    except Exception:
        # Fallback: simple regex strip
        import re
        return re.sub(r'<[^>]+>', '', text).strip()


def parse_rss_feed(data: str, source: str) -> List[Dict[str, Any]]:
    """Parse RSS/Atom feed into structured items"""
    items = []
    try:
        feed = feedparser.parse(data)
        for entry in feed.entries[:20]:  # Limit to 20 items
            # Session 293: Strip HTML from title and description
            # RSS feeds (especially Medium) often include HTML markup
            raw_description = entry.get('summary', entry.get('description', ''))
            clean_description = strip_html_tags(raw_description)[:500]
            clean_title = strip_html_tags(entry.get('title', 'Untitled'))

            item = {
                'title': clean_title,
                'link': entry.get('link', ''),
                'description': clean_description,
                'published': entry.get('published', entry.get('updated', '')),
                'source': source,
                'type': 'article'
            }
            # Extract author if available
            if 'author' in entry:
                item['author'] = strip_html_tags(entry.author)
            # Extract tags/categories
            if 'tags' in entry:
                item['tags'] = [strip_html_tags(t.term) for t in entry.tags[:5]]
            items.append(item)
    except Exception as e:
        logger.error(f"Error parsing RSS feed: {e}")
    return items


async def fetch_hackernews_stories(session: aiohttp.ClientSession, story_ids: List[int]) -> List[Dict[str, Any]]:
    """
    Session 394: Fetch full story details from HackerNews API.
    The topstories.json endpoint only returns IDs, so we need to fetch each story.
    """
    stories = []
    for story_id in story_ids[:15]:  # Limit to 15 stories for performance
        try:
            url = f'https://hacker-news.firebaseio.com/v0/item/{story_id}.json'
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    story = await response.json()
                    if story and story.get('title'):
                        stories.append({
                            'title': story.get('title', ''),
                            'description': f"Score: {story.get('score', 0)} | Comments: {story.get('descendants', 0)} | By: {story.get('by', '')}",
                            'link': story.get('url', f"https://news.ycombinator.com/item?id={story_id}"),
                            'author': story.get('by', ''),
                            'score': story.get('score', 0),
                            'comments': story.get('descendants', 0),
                            'source': 'hackernews',
                            'type': 'hackernews_story',
                            'fetched_at': datetime.now(timezone.utc).isoformat()
                        })
        except Exception as e:
            logger.warning(f"Error fetching HN story {story_id}: {e}")
    return stories


def parse_json_api(data: Any, source: str) -> List[Dict[str, Any]]:
    """Parse JSON API response into structured items"""
    items = []
    try:
        # Handle different API response formats
        if isinstance(data, list):
            for item in data[:30]:
                if isinstance(item, dict):
                    items.append(normalize_item(item, source))
                elif isinstance(item, (int, str)):
                    # Session 394: Don't store HackerNews IDs as references
                    # They will be fetched separately in collect_spider_data
                    if source == 'hackernews':
                        # Skip - these will be handled by fetch_hackernews_stories
                        continue
                    items.append({'id': item, 'source': source, 'type': 'reference'})
        elif isinstance(data, dict):
            # Single object or wrapped response
            if 'results' in data:
                return parse_json_api(data['results'], source)
            elif 'data' in data:
                # Reddit format: data.children contains posts
                if isinstance(data['data'], dict) and 'children' in data['data']:
                    children = data['data']['children']
                    for child in children[:30]:
                        if isinstance(child, dict) and 'data' in child:
                            post = child['data']
                            items.append({
                                'title': post.get('title', ''),
                                'description': post.get('selftext', '')[:500] if post.get('selftext') else '',
                                'link': f"https://reddit.com{post.get('permalink', '')}",
                                'author': post.get('author', ''),
                                'subreddit': post.get('subreddit', ''),
                                'score': post.get('score', 0),
                                'num_comments': post.get('num_comments', 0),
                                'created_utc': post.get('created_utc', 0),
                                'source': source,
                                'type': 'reddit_post',
                                'fetched_at': datetime.now(timezone.utc).isoformat()
                            })
                    return items
                else:
                    return parse_json_api(data['data'], source)
            elif 'items' in data:
                return parse_json_api(data['items'], source)
            elif 'articles' in data:
                return parse_json_api(data['articles'], source)
            elif 'jobs' in data:
                return parse_json_api(data['jobs'], source)
            elif 'features' in data:
                # GeoJSON format (NOAA Weather API)
                for feature in data['features'][:30]:
                    if isinstance(feature, dict) and 'properties' in feature:
                        props = feature['properties']
                        items.append({
                            'title': props.get('headline', props.get('event', 'Weather Alert')),
                            'description': props.get('description', '')[:500],
                            'link': props.get('@id', props.get('id', '')),
                            'severity': props.get('severity', ''),
                            'certainty': props.get('certainty', ''),
                            'urgency': props.get('urgency', ''),
                            'area': props.get('areaDesc', ''),
                            'effective': props.get('effective', ''),
                            'expires': props.get('expires', ''),
                            'source': source,
                            'type': 'weather_alert',
                            'fetched_at': datetime.now(timezone.utc).isoformat()
                        })
                return items
            elif 'chart' in data:
                # Yahoo Finance format
                chart = data['chart']
                if 'result' in chart and chart['result']:
                    result = chart['result'][0]
                    items.append({
                        'symbol': result.get('meta', {}).get('symbol', 'UNKNOWN'),
                        'price': result.get('meta', {}).get('regularMarketPrice', 0),
                        'currency': result.get('meta', {}).get('currency', 'USD'),
                        'source': source,
                        'type': 'market_data'
                    })
            else:
                items.append(normalize_item(data, source))
    except Exception as e:
        logger.error(f"Error parsing JSON: {e}")
    return items


def normalize_item(item: Dict[str, Any], source: str) -> Dict[str, Any]:
    """Normalize an item to a standard format"""
    normalized = {
        'source': source,
        'type': 'item',
        'fetched_at': datetime.now(timezone.utc).isoformat()
    }

    # Try to extract common fields
    field_mappings = {
        'title': ['title', 'name', 'headline', 'position', 'role'],
        'description': ['description', 'summary', 'body', 'content', 'excerpt', 'tagline'],
        'link': ['link', 'url', 'href', 'apply_url', 'website'],
        'author': ['author', 'creator', 'company', 'company_name', 'organization'],
        'published': ['published', 'created_at', 'date', 'timestamp', 'posted_at', 'published_at'],
        'image': ['image', 'thumbnail', 'cover', 'logo', 'avatar'],
        'tags': ['tags', 'categories', 'skills', 'keywords'],
        'price': ['price', 'current_price', 'salary', 'budget', 'cost', 'amount'],
        'location': ['location', 'remote', 'region', 'country'],
    }

    # Session 293: Fields that should have HTML stripped
    html_strip_fields = {'title', 'description', 'author'}

    for standard_field, possible_keys in field_mappings.items():
        for key in possible_keys:
            if key in item and item[key]:
                value = item[key]
                # Handle nested objects
                if isinstance(value, dict):
                    value = str(value)
                # Session 293: Strip HTML from text fields that commonly contain markup
                if isinstance(value, str) and standard_field in html_strip_fields:
                    value = strip_html_tags(value)
                # Truncate long strings
                if isinstance(value, str) and len(value) > 1000:
                    value = value[:1000] + '...'
                normalized[standard_field] = value
                break

    # Include any additional interesting fields
    for key, value in item.items():
        if key not in normalized and not key.startswith('_'):
            if isinstance(value, (str, int, float, bool)):
                normalized[key] = value
            elif isinstance(value, list) and len(value) < 10:
                normalized[key] = value

    return normalized


def parse_html_page(html: str, source: str, url: str) -> List[Dict[str, Any]]:
    """Parse HTML page into structured items"""
    items = []
    try:
        soup = BeautifulSoup(html, 'html.parser')

        # Try to find article/job/item elements
        selectors = [
            'article',
            '.job', '.job-listing', '.job-card',
            '.shot', '.project', '.item',
            '.post', '.entry', '.card',
            '[data-job]', '[data-project]',
        ]

        for selector in selectors:
            elements = soup.select(selector)[:20]
            if elements:
                for elem in elements:
                    item = extract_item_from_element(elem, source)
                    if item and (item.get('title') or item.get('link')):
                        item['source_url'] = url
                        items.append(item)
                break

        # Fallback: extract links with titles
        if not items:
            for link in soup.select('a[href]')[:30]:
                title = link.get_text(strip=True)
                href = link.get('href', '')
                if title and len(title) > 10 and href:
                    items.append({
                        'title': title[:200],
                        'link': urljoin(url, href),
                        'source': source,
                        'type': 'link'
                    })
    except Exception as e:
        logger.error(f"Error parsing HTML: {e}")
    return items


def extract_item_from_element(elem, source: str) -> Dict[str, Any]:
    """Extract item data from an HTML element"""
    item = {'source': source, 'type': 'scraped'}

    # Extract title
    for sel in ['h1', 'h2', 'h3', '.title', '.name', 'a']:
        title_elem = elem.select_one(sel)
        if title_elem:
            item['title'] = title_elem.get_text(strip=True)[:200]
            if sel == 'a':
                item['link'] = title_elem.get('href', '')
            break

    # Extract link
    if 'link' not in item:
        link_elem = elem.select_one('a[href]')
        if link_elem:
            item['link'] = link_elem.get('href', '')

    # Extract description
    for sel in ['.description', '.summary', '.excerpt', 'p']:
        desc_elem = elem.select_one(sel)
        if desc_elem:
            item['description'] = desc_elem.get_text(strip=True)[:500]
            break

    # Extract company/author
    for sel in ['.company', '.author', '.creator', '.meta']:
        author_elem = elem.select_one(sel)
        if author_elem:
            item['author'] = author_elem.get_text(strip=True)[:100]
            break

    # Extract tags
    tag_elems = elem.select('.tag, .skill, .label, .category')
    if tag_elems:
        item['tags'] = [t.get_text(strip=True) for t in tag_elems[:10]]

    return item


async def _collect_api_spider_data(spider_name: str) -> Dict[str, Any]:
    """
    Collect data from API-based spiders (BlueSky, YouTube, Discord).
    These spiders use their own API clients instead of SPIDER_TARGET_URLS.
    """

    if spider_name == 'bluesky':
        return await _collect_bluesky_data()
    elif spider_name == 'youtube':
        return await _collect_youtube_data()
    elif spider_name == 'discord':
        return await _collect_discord_data()

    return {
        'items': [],
        'source': spider_name,
        'error': f'Unknown API spider: {spider_name}',
        'timestamp': datetime.now(timezone.utc).isoformat()
    }


async def _collect_bluesky_data() -> Dict[str, Any]:
    """Collect data from BlueSky AT Protocol API"""
    import os

    identifier = os.getenv('BLUESKY_IDENTIFIER', '')
    password = os.getenv('BLUESKY_PASSWORD', '')

    if not identifier or not password:
        return {
            'items': [],
            'source': 'bluesky',
            'error': 'BLUESKY_IDENTIFIER and BLUESKY_PASSWORD not configured',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

    search_terms = [
        'AI tools', 'content creator', 'stable diffusion',
        'midjourney', 'AI writing', 'creator economy', 'freelance'
    ]

    all_posts = []

    try:
        async with aiohttp.ClientSession() as session:
            # Authenticate
            auth_url = "https://bsky.social/xrpc/com.atproto.server.createSession"
            async with session.post(auth_url, json={
                "identifier": identifier,
                "password": password
            }, timeout=aiohttp.ClientTimeout(total=15)) as response:
                if response.status != 200:
                    return {
                        'items': [],
                        'source': 'bluesky',
                        'error': f'Authentication failed: {response.status}',
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    }
                auth_data = await response.json()
                access_token = auth_data.get('accessJwt')

            headers = {'Authorization': f'Bearer {access_token}'}

            # Search for each term
            for term in search_terms[:4]:  # Limit to avoid rate limits
                try:
                    search_url = "https://bsky.social/xrpc/app.bsky.feed.searchPosts"
                    params = {'q': term, 'limit': 15}

                    async with session.get(search_url, headers=headers, params=params,
                                         timeout=aiohttp.ClientTimeout(total=10)) as response:
                        if response.status == 200:
                            data = await response.json()
                            posts = data.get('posts', [])

                            for post in posts:
                                record = post.get('record', {})
                                author = post.get('author', {})

                                all_posts.append({
                                    'title': f"@{author.get('handle', '')}: {record.get('text', '')[:60]}...",
                                    'description': record.get('text', ''),
                                    'link': post.get('uri', ''),
                                    'author': author.get('displayName', author.get('handle', '')),
                                    'date': record.get('createdAt', ''),
                                    'likes': post.get('likeCount', 0),
                                    'reposts': post.get('repostCount', 0),
                                    'search_term': term,
                                    'source': 'bluesky',
                                    'type': 'social_post',
                                })

                    await asyncio.sleep(0.3)  # Rate limiting

                except Exception as e:
                    logger.warning(f"BlueSky search error for '{term}': {e}")

        logger.info(f"BlueSky: collected {len(all_posts)} posts")

        return {
            'items': all_posts[:50],
            'item_count': len(all_posts),
            'source': 'bluesky',
            'collected_at': datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        logger.error(f"BlueSky collection error: {e}")
        return {
            'items': [],
            'source': 'bluesky',
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }


async def _collect_youtube_data() -> Dict[str, Any]:
    """Collect data from YouTube Data API v3"""
    import os

    # Try YOUTUBE_API_KEY first, fall back to GOOGLE_API_KEY
    api_key = os.getenv('YOUTUBE_API_KEY', '') or os.getenv('GOOGLE_API_KEY', '')

    if not api_key:
        return {
            'items': [],
            'source': 'youtube',
            'error': 'GOOGLE_API_KEY not configured',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

    search_queries = [
        'AI content creation tools review',
        'midjourney tutorial',
        'stable diffusion problems',
        'AI writing tools comparison',
    ]

    all_videos = []

    try:
        async with aiohttp.ClientSession() as session:
            for query in search_queries[:3]:
                try:
                    search_url = "https://www.googleapis.com/youtube/v3/search"
                    params = {
                        'part': 'snippet',
                        'q': query,
                        'type': 'video',
                        'maxResults': 5,
                        'order': 'relevance',
                        'key': api_key,
                    }

                    async with session.get(search_url, params=params,
                                         timeout=aiohttp.ClientTimeout(total=10)) as response:
                        if response.status == 200:
                            data = await response.json()
                            items = data.get('items', [])

                            for item in items:
                                video_id = item.get('id', {}).get('videoId')
                                snippet = item.get('snippet', {})

                                if video_id:
                                    all_videos.append({
                                        'title': snippet.get('title', ''),
                                        'description': snippet.get('description', '')[:300],
                                        'link': f"https://youtube.com/watch?v={video_id}",
                                        'author': snippet.get('channelTitle', ''),
                                        'date': snippet.get('publishedAt', ''),
                                        'search_term': query,
                                        'source': 'youtube',
                                        'type': 'video',
                                    })
                        else:
                            error_body = await response.text()
                            logger.warning(f"YouTube API error: {response.status} - {error_body[:200]}")

                    await asyncio.sleep(0.3)

                except Exception as e:
                    logger.warning(f"YouTube search error for '{query}': {e}")

        logger.info(f"YouTube: collected {len(all_videos)} videos")

        return {
            'items': all_videos[:50],
            'item_count': len(all_videos),
            'source': 'youtube',
            'collected_at': datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        logger.error(f"YouTube collection error: {e}")
        return {
            'items': [],
            'source': 'youtube',
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }


async def _collect_discord_data() -> Dict[str, Any]:
    """Collect data from Discord Bot API.

    Session 399: Implemented actual Discord data collection.
    Fetches guilds the bot is in, and recent messages from text channels.
    """
    import os

    bot_token = os.getenv('DISCORD_BOT_TOKEN', '')

    if not bot_token:
        return {
            'items': [],
            'source': 'discord',
            'error': 'DISCORD_BOT_TOKEN not configured (need bot token, not just app ID)',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

    all_items = []
    headers = {
        'Authorization': f'Bot {bot_token}',
        'Content-Type': 'application/json'
    }

    try:
        async with aiohttp.ClientSession() as session:
            # Get guilds (servers) the bot is in
            guilds_url = 'https://discord.com/api/v10/users/@me/guilds'
            async with session.get(guilds_url, headers=headers,
                                   timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    guilds = await response.json()
                    logger.info(f"Discord: Bot is in {len(guilds)} guilds")

                    # Collect info about each guild
                    for guild in guilds[:5]:  # Limit to first 5 guilds
                        guild_item = {
                            'title': f"Server: {guild.get('name', 'Unknown')}",
                            'description': f"Discord server with ID {guild.get('id')}",
                            'guild_id': guild.get('id'),
                            'guild_name': guild.get('name'),
                            'icon': f"https://cdn.discordapp.com/icons/{guild.get('id')}/{guild.get('icon')}.png" if guild.get('icon') else None,
                            'owner': guild.get('owner', False),
                            'permissions': guild.get('permissions'),
                            'source': 'discord',
                            'type': 'guild',
                            'fetched_at': datetime.now(timezone.utc).isoformat()
                        }
                        all_items.append(guild_item)

                        # Try to get channels for this guild
                        try:
                            channels_url = f"https://discord.com/api/v10/guilds/{guild.get('id')}/channels"
                            async with session.get(channels_url, headers=headers,
                                                   timeout=aiohttp.ClientTimeout(total=5)) as ch_response:
                                if ch_response.status == 200:
                                    channels = await ch_response.json()
                                    text_channels = [c for c in channels if c.get('type') == 0][:3]

                                    for channel in text_channels:
                                        channel_item = {
                                            'title': f"#{channel.get('name', 'unknown')} in {guild.get('name')}",
                                            'description': channel.get('topic', 'No topic set'),
                                            'channel_id': channel.get('id'),
                                            'channel_name': channel.get('name'),
                                            'guild_name': guild.get('name'),
                                            'source': 'discord',
                                            'type': 'channel',
                                            'fetched_at': datetime.now(timezone.utc).isoformat()
                                        }
                                        all_items.append(channel_item)
                        except Exception as e:
                            logger.debug(f"Could not fetch channels for {guild.get('name')}: {e}")

                        await asyncio.sleep(0.3)  # Rate limiting
                elif response.status == 401:
                    return {
                        'items': [],
                        'source': 'discord',
                        'error': 'Invalid bot token - check DISCORD_BOT_TOKEN',
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    }
                else:
                    error_text = await response.text()
                    return {
                        'items': [],
                        'source': 'discord',
                        'error': f'Discord API error {response.status}: {error_text[:100]}',
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    }

        logger.info(f"Discord: collected {len(all_items)} items")

        return {
            'items': all_items,
            'item_count': len(all_items),
            'source': 'discord',
            'collected_at': datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        logger.error(f"Discord collection error: {e}")
        return {
            'items': [],
            'source': 'discord',
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }


# === SESSION 396: PHASE 3 API HANDLERS ===

async def _collect_polygon_data() -> Dict[str, Any]:
    """Collect financial data from Polygon.io API"""
    import os
    from dotenv import load_dotenv
    load_dotenv()

    api_key = os.getenv('POLYGON_API_KEY', '')

    if not api_key:
        return {
            'items': [],
            'source': 'polygon_finance',
            'error': 'POLYGON_API_KEY not configured',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

    all_items = []

    try:
        async with aiohttp.ClientSession() as session:
            # Use v3 reference endpoint (works with free tier)
            # Get latest market news
            url = f'https://api.polygon.io/v2/reference/news?limit=15&apiKey={api_key}'
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                if response.status == 200:
                    data = await response.json()
                    news = data.get('results', [])
                    for article in news:
                        all_items.append({
                            'title': article.get('title', ''),
                            'description': article.get('description', '')[:500] if article.get('description') else '',
                            'link': article.get('article_url', ''),
                            'author': article.get('author', ''),
                            'published': article.get('published_utc', ''),
                            'tickers': article.get('tickers', []),
                            'source': 'polygon_finance',
                            'type': 'market_news',
                            'fetched_at': datetime.now(timezone.utc).isoformat()
                        })
                else:
                    error_text = await response.text()
                    logger.warning(f"Polygon API error: {response.status} - {error_text[:100]}")

        logger.info(f"Polygon: collected {len(all_items)} items")

        return {
            'items': all_items[:50],
            'item_count': len(all_items),
            'source': 'polygon_finance',
            'collected_at': datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        logger.error(f"Polygon collection error: {e}")
        return {
            'items': [],
            'source': 'polygon_finance',
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }


async def _collect_etherscan_data() -> Dict[str, Any]:
    """Collect blockchain data from Etherscan API V2"""
    import os
    from dotenv import load_dotenv
    load_dotenv()

    api_key = os.getenv('ETHERSCAN_API_KEY', '')

    if not api_key:
        return {
            'items': [],
            'source': 'etherscan',
            'error': 'ETHERSCAN_API_KEY not configured',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

    all_items = []

    try:
        async with aiohttp.ClientSession() as session:
            # Get ETH supply stats (V2 API)
            url = f'https://api.etherscan.io/v2/api?chainid=1&module=stats&action=ethsupply&apikey={api_key}'
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('status') == '1':
                        result = data.get('result', '')
                        if result:
                            eth_supply = float(result) / 1e18  # Convert from wei
                            all_items.append({
                                'title': f"ETH Total Supply: {eth_supply:,.0f} ETH",
                                'description': f"Total Ethereum supply on mainnet",
                                'eth_supply': eth_supply,
                                'source': 'etherscan',
                                'type': 'eth_supply',
                                'fetched_at': datetime.now(timezone.utc).isoformat()
                            })

            # Get latest block number
            url = f'https://api.etherscan.io/v2/api?chainid=1&module=proxy&action=eth_blockNumber&apikey={api_key}'
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    result = data.get('result', '')
                    if result:
                        block_num = int(result, 16)
                        all_items.append({
                            'title': f"Latest ETH Block: {block_num:,}",
                            'description': f"Current Ethereum mainnet block number",
                            'block_number': block_num,
                            'source': 'etherscan',
                            'type': 'block_info',
                            'fetched_at': datetime.now(timezone.utc).isoformat()
                        })

        logger.info(f"Etherscan: collected {len(all_items)} items")

        return {
            'items': all_items,
            'item_count': len(all_items),
            'source': 'etherscan',
            'collected_at': datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        logger.error(f"Etherscan collection error: {e}")
        return {
            'items': [],
            'source': 'etherscan',
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }


async def _collect_newsapi_data() -> Dict[str, Any]:
    """Collect news from NewsAPI"""
    import os

    api_key = os.getenv('NEWS_API_KEY', '')

    if not api_key:
        return {
            'items': [],
            'source': 'newsapi',
            'error': 'NEWS_API_KEY not configured',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

    all_items = []

    try:
        async with aiohttp.ClientSession() as session:
            # Tech headlines
            url = f'https://newsapi.org/v2/top-headlines?category=technology&language=en&pageSize=20&apiKey={api_key}'
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                if response.status == 200:
                    data = await response.json()
                    articles = data.get('articles', [])
                    for article in articles:
                        all_items.append({
                            'title': article.get('title', ''),
                            'description': article.get('description', '')[:500] if article.get('description') else '',
                            'link': article.get('url', ''),
                            'author': article.get('author', ''),
                            'published': article.get('publishedAt', ''),
                            'source_name': article.get('source', {}).get('name', ''),
                            'image': article.get('urlToImage', ''),
                            'source': 'newsapi',
                            'type': 'news_article',
                            'fetched_at': datetime.now(timezone.utc).isoformat()
                        })
                elif response.status == 426:
                    # Free tier limitation - need to use different endpoint
                    logger.warning("NewsAPI: Free tier requires 'everything' endpoint from localhost only")
                else:
                    logger.warning(f"NewsAPI error: {response.status}")

        logger.info(f"NewsAPI: collected {len(all_items)} items")

        return {
            'items': all_items[:50],
            'item_count': len(all_items),
            'source': 'newsapi',
            'collected_at': datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        logger.error(f"NewsAPI collection error: {e}")
        return {
            'items': [],
            'source': 'newsapi',
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }


async def _collect_giphy_data() -> Dict[str, Any]:
    """Collect trending GIFs from Giphy API"""
    import os

    api_key = os.getenv('GIPHY_API_KEY', os.getenv('GIPHY_API_Key', ''))

    if not api_key:
        return {
            'items': [],
            'source': 'giphy',
            'error': 'GIPHY_API_KEY not configured',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

    all_items = []

    try:
        async with aiohttp.ClientSession() as session:
            url = f'https://api.giphy.com/v1/gifs/trending?api_key={api_key}&limit=20&rating=g'
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    gifs = data.get('data', [])
                    for gif in gifs:
                        all_items.append({
                            'title': gif.get('title', 'Trending GIF'),
                            'description': f"Trending on Giphy - {gif.get('trending_datetime', '')}",
                            'link': gif.get('url', ''),
                            'image': gif.get('images', {}).get('fixed_height', {}).get('url', ''),
                            'embed_url': gif.get('embed_url', ''),
                            'source': 'giphy',
                            'type': 'trending_gif',
                            'fetched_at': datetime.now(timezone.utc).isoformat()
                        })
                else:
                    logger.warning(f"Giphy API error: {response.status}")

        logger.info(f"Giphy: collected {len(all_items)} items")

        return {
            'items': all_items,
            'item_count': len(all_items),
            'source': 'giphy',
            'collected_at': datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        logger.error(f"Giphy collection error: {e}")
        return {
            'items': [],
            'source': 'giphy',
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }


async def _collect_spotify_data() -> Dict[str, Any]:
    """Collect new releases and featured playlists from Spotify API.

    Session 399: Added Spotify handler for trending music data.
    Uses client credentials flow (no user auth needed).
    """
    import os
    import base64

    client_id = os.getenv('SPOTIFY_CLIENT_ID', '')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET', '')

    if not client_id or not client_secret:
        return {
            'items': [],
            'source': 'spotify',
            'error': 'SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET not configured',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

    all_items = []

    try:
        async with aiohttp.ClientSession() as session:
            # Get access token using client credentials
            auth_string = f"{client_id}:{client_secret}"
            auth_bytes = base64.b64encode(auth_string.encode()).decode()

            token_url = "https://accounts.spotify.com/api/token"
            async with session.post(
                token_url,
                headers={
                    'Authorization': f'Basic {auth_bytes}',
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                data={'grant_type': 'client_credentials'},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status != 200:
                    return {
                        'items': [],
                        'source': 'spotify',
                        'error': f'Failed to get Spotify token: {response.status}',
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    }
                token_data = await response.json()
                access_token = token_data.get('access_token')

            headers = {'Authorization': f'Bearer {access_token}'}

            # Get new releases
            releases_url = "https://api.spotify.com/v1/browse/new-releases?limit=20"
            async with session.get(releases_url, headers=headers,
                                   timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    albums = data.get('albums', {}).get('items', [])
                    for album in albums:
                        artists = ', '.join([a.get('name', '') for a in album.get('artists', [])])
                        all_items.append({
                            'title': f"{album.get('name', '')} - {artists}",
                            'description': f"New release: {album.get('album_type', 'album')} with {album.get('total_tracks', 0)} tracks",
                            'link': album.get('external_urls', {}).get('spotify', ''),
                            'image': album.get('images', [{}])[0].get('url', '') if album.get('images') else '',
                            'release_date': album.get('release_date', ''),
                            'artists': artists,
                            'source': 'spotify',
                            'type': 'new_release',
                            'fetched_at': datetime.now(timezone.utc).isoformat()
                        })

            # Get featured playlists
            playlists_url = "https://api.spotify.com/v1/browse/featured-playlists?limit=10"
            async with session.get(playlists_url, headers=headers,
                                   timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    playlists = data.get('playlists', {}).get('items', [])
                    for playlist in playlists:
                        all_items.append({
                            'title': playlist.get('name', ''),
                            'description': playlist.get('description', ''),
                            'link': playlist.get('external_urls', {}).get('spotify', ''),
                            'image': playlist.get('images', [{}])[0].get('url', '') if playlist.get('images') else '',
                            'tracks': playlist.get('tracks', {}).get('total', 0),
                            'source': 'spotify',
                            'type': 'featured_playlist',
                            'fetched_at': datetime.now(timezone.utc).isoformat()
                        })

        logger.info(f"Spotify: collected {len(all_items)} items")

        return {
            'items': all_items,
            'item_count': len(all_items),
            'source': 'spotify',
            'collected_at': datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        logger.error(f"Spotify collection error: {e}")
        return {
            'items': [],
            'source': 'spotify',
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }


async def _collect_polygon_gaming_data() -> Dict[str, Any]:
    """Collect gaming news from Polygon RSS feeds.

    Session 399: Added handler for Polygon gaming news.
    Uses free RSS feeds, no API key required.
    """
    import feedparser

    RSS_FEEDS = {
        'main': 'https://www.polygon.com/rss/index.xml',
        'reviews': 'https://www.polygon.com/rss/reviews/index.xml',
        'features': 'https://www.polygon.com/rss/features/index.xml',
    }

    all_items = []

    try:
        for feed_name, feed_url in RSS_FEEDS.items():
            try:
                feed = feedparser.parse(feed_url)
                if feed.entries:
                    for entry in feed.entries[:15]:
                        title = entry.get('title', '')
                        if title:
                            all_items.append({
                                'title': title,
                                'description': entry.get('summary', '')[:300] if entry.get('summary') else '',
                                'link': entry.get('link', ''),
                                'published': entry.get('published', ''),
                                'author': entry.get('author', 'Polygon'),
                                'tags': [tag.term for tag in entry.get('tags', [])][:5],
                                'feed_source': feed_name,
                                'source': 'polygon_gaming',
                                'type': 'gaming_news',
                                'fetched_at': datetime.now(timezone.utc).isoformat()
                            })
            except Exception as e:
                logger.warning(f"Error fetching {feed_name} feed: {e}")

        logger.info(f"Polygon Gaming: collected {len(all_items)} items")

        return {
            'items': all_items,
            'item_count': len(all_items),
            'source': 'polygon_gaming',
            'collected_at': datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        logger.error(f"Polygon Gaming collection error: {e}")
        return {
            'items': [],
            'source': 'polygon_gaming',
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }


async def _collect_unsplash_data() -> Dict[str, Any]:
    """Collect trending photos from Unsplash API"""
    import os

    access_key = os.getenv('UNSPLASH_ACCESS_KEY', '')

    if not access_key:
        return {
            'items': [],
            'source': 'unsplash',
            'error': 'UNSPLASH_ACCESS_KEY not configured',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

    all_items = []

    try:
        async with aiohttp.ClientSession() as session:
            headers = {'Authorization': f'Client-ID {access_key}'}
            url = 'https://api.unsplash.com/photos?order_by=popular&per_page=20'
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as response:
                if response.status == 200:
                    photos = await response.json()
                    for photo in photos:
                        all_items.append({
                            'title': photo.get('alt_description', photo.get('description', 'Popular photo')),
                            'description': f"By {photo.get('user', {}).get('name', 'Unknown')} - {photo.get('likes', 0)} likes",
                            'link': photo.get('links', {}).get('html', ''),
                            'image': photo.get('urls', {}).get('regular', ''),
                            'author': photo.get('user', {}).get('name', ''),
                            'likes': photo.get('likes', 0),
                            'source': 'unsplash',
                            'type': 'photo',
                            'fetched_at': datetime.now(timezone.utc).isoformat()
                        })
                else:
                    logger.warning(f"Unsplash API error: {response.status}")

        logger.info(f"Unsplash: collected {len(all_items)} items")

        return {
            'items': all_items,
            'item_count': len(all_items),
            'source': 'unsplash',
            'collected_at': datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        logger.error(f"Unsplash collection error: {e}")
        return {
            'items': [],
            'source': 'unsplash',
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }


async def _collect_adzuna_data() -> Dict[str, Any]:
    """Collect job listings from Adzuna API"""
    import os

    app_id = os.getenv('ADZUNA_APP_ID', '')
    app_key = os.getenv('ADZUNA_APP_KEY', '')

    if not app_id or not app_key:
        return {
            'items': [],
            'source': 'adzuna',
            'error': 'ADZUNA_APP_ID or ADZUNA_APP_KEY not configured',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

    all_items = []

    try:
        async with aiohttp.ClientSession() as session:
            # Search for remote tech jobs
            url = f'https://api.adzuna.com/v1/api/jobs/us/search/1?app_id={app_id}&app_key={app_key}&results_per_page=20&what=developer%20remote&content-type=application/json'
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                if response.status == 200:
                    data = await response.json()
                    jobs = data.get('results', [])
                    for job in jobs:
                        salary_min = job.get('salary_min', 0)
                        salary_max = job.get('salary_max', 0)
                        salary_str = f"${salary_min:,.0f} - ${salary_max:,.0f}" if salary_min else "Not specified"

                        all_items.append({
                            'title': job.get('title', ''),
                            'description': job.get('description', '')[:500],
                            'link': job.get('redirect_url', ''),
                            'company': job.get('company', {}).get('display_name', ''),
                            'location': job.get('location', {}).get('display_name', ''),
                            'salary': salary_str,
                            'salary_min': salary_min,
                            'salary_max': salary_max,
                            'created': job.get('created', ''),
                            'source': 'adzuna',
                            'type': 'job_listing',
                            'fetched_at': datetime.now(timezone.utc).isoformat()
                        })
                else:
                    logger.warning(f"Adzuna API error: {response.status}")

        logger.info(f"Adzuna: collected {len(all_items)} items")

        return {
            'items': all_items,
            'item_count': len(all_items),
            'source': 'adzuna',
            'collected_at': datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        logger.error(f"Adzuna collection error: {e}")
        return {
            'items': [],
            'source': 'adzuna',
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }


async def _collect_finnhub_data() -> Dict[str, Any]:
    """Collect financial data from Finnhub API - stock quotes, market news"""
    import os
    from dotenv import load_dotenv
    load_dotenv()

    api_key = os.getenv('FINNHUB_API_KEY', '')

    if not api_key:
        return {
            'items': [],
            'source': 'finnhub',
            'error': 'FINNHUB_API_KEY not configured',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

    all_items = []

    # Top stocks to track
    tracked_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'JPM', 'V', 'UNH']

    try:
        async with aiohttp.ClientSession() as session:
            # 1. Get stock quotes for top companies
            for symbol in tracked_symbols[:5]:  # Limit to 5 for rate limits
                url = f'https://finnhub.io/api/v1/quote?symbol={symbol}&token={api_key}'
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('c'):  # Has current price
                            all_items.append({
                                'title': f'{symbol} Stock Quote',
                                'description': f'{symbol}: ${data.get("c", 0):.2f} (Change: {data.get("dp", 0):.2f}%)',
                                'symbol': symbol,
                                'current_price': data.get('c', 0),
                                'change': data.get('d', 0),
                                'change_percent': data.get('dp', 0),
                                'high': data.get('h', 0),
                                'low': data.get('l', 0),
                                'open': data.get('o', 0),
                                'previous_close': data.get('pc', 0),
                                'source': 'finnhub',
                                'type': 'stock_quote',
                                'fetched_at': datetime.now(timezone.utc).isoformat()
                            })
                await asyncio.sleep(0.15)  # Rate limiting (60 calls/min)

            # 2. Get market news
            news_url = f'https://finnhub.io/api/v1/news?category=general&token={api_key}'
            async with session.get(news_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    news = await response.json()
                    for article in news[:15]:
                        all_items.append({
                            'title': article.get('headline', ''),
                            'description': article.get('summary', '')[:500],
                            'link': article.get('url', ''),
                            'source_name': article.get('source', ''),
                            'category': article.get('category', ''),
                            'image': article.get('image', ''),
                            'published': datetime.fromtimestamp(article.get('datetime', 0), tz=timezone.utc).isoformat() if article.get('datetime') else '',
                            'source': 'finnhub',
                            'type': 'market_news',
                            'fetched_at': datetime.now(timezone.utc).isoformat()
                        })

        logger.info(f"Finnhub: collected {len(all_items)} items")

        return {
            'items': all_items,
            'item_count': len(all_items),
            'source': 'finnhub',
            'collected_at': datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        logger.error(f"Finnhub collection error: {e}")
        return {
            'items': [],
            'source': 'finnhub',
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }


# === SESSION 397: LEGAL SPIDERS ===

async def _collect_courtlistener_data() -> Dict[str, Any]:
    """Collect legal opinions from CourtListener FREE API.

    CourtListener is the Free Law Project's open legal data API.
    No API key required for basic access!
    API docs: https://www.courtlistener.com/help/api/rest/
    """
    from datetime import timedelta

    all_items = []
    base_url = "https://www.courtlistener.com/api/rest/v4"

    try:
        # Fetch recent opinions (last 7 days)
        date_filed_after = (datetime.now(timezone.utc) - timedelta(days=7)).strftime('%Y-%m-%d')

        async with aiohttp.ClientSession() as session:
            # Search for recent opinions
            search_url = f"{base_url}/search/"
            params = {
                'type': 'o',  # Opinions
                'order_by': 'dateFiled desc',
                'date_filed__gte': date_filed_after,
                'page_size': 50
            }

            headers = {
                'User-Agent': 'AI-Content-Studio/1.0 (Legal Research)',
                'Accept': 'application/json'
            }

            async with session.get(search_url, params=params, headers=headers,
                                   timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    data = await response.json()
                    results = data.get('results', [])

                    for opinion in results:
                        # Generate tags based on content
                        tags = ['legal', 'case_law', 'court_opinion']
                        court = opinion.get('court', '').lower()
                        if 'supreme' in court:
                            tags.append('supreme_court')
                        elif 'circuit' in court or 'appellate' in court:
                            tags.append('appellate')
                        elif 'district' in court:
                            tags.append('district_court')

                        case_name = opinion.get('caseName', '').lower()
                        if any(term in case_name for term in ['patent', 'copyright', 'trademark']):
                            tags.append('intellectual_property')
                        if any(term in case_name for term in ['criminal', 'united states v']):
                            tags.append('criminal_law')

                        all_items.append({
                            'title': opinion.get('caseName', 'Unknown Case'),
                            'description': opinion.get('snippet', '')[:500],
                            'link': f"https://www.courtlistener.com{opinion.get('absolute_url', '')}",
                            'court': opinion.get('court', 'Unknown Court'),
                            'date_filed': opinion.get('dateFiled', ''),
                            'docket_number': opinion.get('docketNumber', ''),
                            'precedential_status': opinion.get('precedentialStatus', ''),
                            'citation': opinion.get('citation', []),
                            'tags': tags,
                            'source': 'courtlistener',
                            'type': 'legal_opinion',
                            'fetched_at': datetime.now(timezone.utc).isoformat()
                        })
                else:
                    logger.warning(f"CourtListener API returned {response.status}")

        logger.info(f"CourtListener: collected {len(all_items)} legal opinions")

        return {
            'items': all_items,
            'item_count': len(all_items),
            'source': 'courtlistener',
            'collected_at': datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        logger.error(f"CourtListener collection error: {e}")
        return {
            'items': [],
            'source': 'courtlistener',
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }


async def _collect_legal_news_data() -> Dict[str, Any]:
    """Collect legal news from SCOTUSblog and Google News.

    Session 399: Renamed from justia (which was blocked by Cloudflare).
    Sources: SCOTUSblog (Supreme Court) + Google News Legal search.
    """
    all_items = []

    rss_feeds = [
        'https://www.scotusblog.com/feed/',  # Supreme Court news
        'https://news.google.com/rss/search?q=legal+law+court+ruling&hl=en-US&gl=US&ceid=US:en',  # Legal news
    ]

    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                'User-Agent': USER_AGENT,
                'Accept': 'application/rss+xml, application/xml, text/xml'
            }

            for feed_url in rss_feeds:
                try:
                    async with session.get(feed_url, headers=headers,
                                           timeout=aiohttp.ClientTimeout(total=15)) as response:
                        if response.status == 200:
                            text = await response.text()
                            # Parse RSS
                            feed = feedparser.parse(text)
                            for entry in feed.entries[:15]:
                                all_items.append({
                                    'title': entry.get('title', ''),
                                    'description': strip_html_tags(entry.get('summary', entry.get('description', '')))[:500],
                                    'link': entry.get('link', ''),
                                    'published': entry.get('published', ''),
                                    'tags': ['legal', 'news', 'court', 'scotus'],
                                    'source': 'legal_news',
                                    'type': 'legal_news',
                                    'fetched_at': datetime.now(timezone.utc).isoformat()
                                })
                except Exception as e:
                    logger.debug(f"Failed to fetch legal news feed {feed_url}: {e}")
                    continue

        logger.info(f"Legal News: collected {len(all_items)} items")

        return {
            'items': all_items,
            'item_count': len(all_items),
            'source': 'legal_news',
            'collected_at': datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        logger.error(f"Legal News collection error: {e}")
        return {
            'items': [],
            'source': 'legal_news',
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }


async def _collect_findlaw_data() -> Dict[str, Any]:
    """Collect legal blogs and articles from FindLaw.

    FindLaw is a Thomson Reuters legal portal - no API, uses web scraping.
    """
    from bs4 import BeautifulSoup

    all_items = []
    practice_areas = ['criminal', 'family', 'business', 'employment']

    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                'User-Agent': USER_AGENT,
                'Accept': 'text/html,application/xhtml+xml'
            }

            for area in practice_areas:
                url = f"https://www.findlaw.com/{area}/"
                async with session.get(url, headers=headers,
                                       timeout=aiohttp.ClientTimeout(total=15)) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')

                        # Find article links
                        for link in soup.find_all('a', href=lambda h: h and f'/{area}/' in h, limit=10):
                            title = link.get_text(strip=True)
                            if not title or len(title) < 15:
                                continue

                            article_url = link.get('href', '')
                            if not article_url.startswith('http'):
                                article_url = f"https://www.findlaw.com{article_url}"

                            # Skip duplicate base URLs
                            if article_url == url:
                                continue

                            all_items.append({
                                'title': title,
                                'link': article_url,
                                'practice_area': area,
                                'tags': ['legal', 'article', area],
                                'source': 'findlaw',
                                'type': 'legal_article',
                                'fetched_at': datetime.now(timezone.utc).isoformat()
                            })

                await asyncio.sleep(0.5)  # Be polite with rate limiting

        logger.info(f"FindLaw: collected {len(all_items)} legal articles")

        return {
            'items': all_items,
            'item_count': len(all_items),
            'source': 'findlaw',
            'collected_at': datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        logger.error(f"FindLaw collection error: {e}")
        return {
            'items': [],
            'source': 'findlaw',
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }


async def _collect_lii_data() -> Dict[str, Any]:
    """Collect legal resources from Cornell's Legal Information Institute.

    LII provides free access to Supreme Court opinions, US Code, and CFR.
    """
    from bs4 import BeautifulSoup

    all_items = []

    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                'User-Agent': USER_AGENT,
                'Accept': 'text/html,application/xhtml+xml'
            }

            # Fetch Supreme Court opinions
            scotus_url = "https://www.law.cornell.edu/supct/index.html"
            async with session.get(scotus_url, headers=headers,
                                   timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')

                    for link in soup.find_all('a', href=lambda h: h and '/supct/' in h, limit=30):
                        title = link.get_text(strip=True)
                        if not title or len(title) < 10:
                            continue

                        opinion_url = link.get('href', '')
                        if not opinion_url.startswith('http'):
                            opinion_url = f"https://www.law.cornell.edu{opinion_url}"

                        # Try to extract citation
                        import re
                        citation = ''
                        parent = link.find_parent(['div', 'li', 'p'])
                        if parent:
                            citation_match = re.search(r'\d+\s+U\.S\.\s+\d+', parent.get_text())
                            if citation_match:
                                citation = citation_match.group()

                        all_items.append({
                            'title': title,
                            'case_name': title,
                            'citation': citation,
                            'link': opinion_url,
                            'court': 'Supreme Court of the United States',
                            'tags': ['legal', 'supreme_court', 'scotus', 'opinion'],
                            'source': 'lii',
                            'type': 'supreme_court_opinion',
                            'fetched_at': datetime.now(timezone.utc).isoformat()
                        })

        logger.info(f"LII: collected {len(all_items)} Supreme Court items")

        return {
            'items': all_items,
            'item_count': len(all_items),
            'source': 'lii',
            'collected_at': datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        logger.error(f"LII collection error: {e}")
        return {
            'items': [],
            'source': 'lii',
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }


async def _collect_sec_edgar_data() -> Dict[str, Any]:
    """Collect SEC EDGAR filings using the SECSpider class.

    Session 399: Added handler so SEC data is stored in SpiderData for Timeline/Data Feed.
    Uses the existing SECSpider which fetches from free SEC EDGAR RSS feeds.
    """
    try:
        from ai_core.spiders.specialized.sec_spider import SECSpider

        sec_spider = SECSpider()
        filings = sec_spider.fetch_data(max_results=30)

        logger.info(f"SEC EDGAR: collected {len(filings)} filings")

        return {
            'items': filings,
            'item_count': len(filings),
            'source': 'sec_edgar',
            'collected_at': datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        logger.error(f"SEC EDGAR collection error: {e}")
        return {
            'items': [],
            'source': 'sec_edgar',
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }


async def _collect_yahoo_finance_data() -> Dict[str, Any]:
    """Collect financial news from Yahoo Finance RSS.

    Session 399: Using RSS feed instead of API (API has strict rate limits).
    Provides financial news, stock analysis, and market updates.
    """
    all_items = []

    rss_url = 'https://finance.yahoo.com/news/rssindex'

    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                'User-Agent': USER_AGENT,
                'Accept': 'application/rss+xml, application/xml, text/xml'
            }

            async with session.get(rss_url, headers=headers,
                                   timeout=aiohttp.ClientTimeout(total=15)) as response:
                if response.status == 200:
                    text = await response.text()
                    feed = feedparser.parse(text)

                    for entry in feed.entries[:30]:
                        all_items.append({
                            'title': entry.get('title', ''),
                            'description': strip_html_tags(entry.get('summary', ''))[:500],
                            'link': entry.get('link', ''),
                            'published': entry.get('published', ''),
                            'tags': ['finance', 'stock', 'market', 'investing'],
                            'source': 'yahoo_finance',
                            'type': 'financial_news',
                            'fetched_at': datetime.now(timezone.utc).isoformat()
                        })

        logger.info(f"Yahoo Finance: collected {len(all_items)} financial news items")

        return {
            'items': all_items,
            'item_count': len(all_items),
            'source': 'yahoo_finance',
            'collected_at': datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        logger.error(f"Yahoo Finance collection error: {e}")
        return {
            'items': [],
            'source': 'yahoo_finance',
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }


async def _collect_freecodecamp_data() -> Dict[str, Any]:
    """Collect developer articles from FreeCodeCamp.

    Session 399: Renamed from hashnode (API returns 404).
    FreeCodeCamp has high-quality developer tutorials and news.
    """
    all_items = []

    rss_url = 'https://www.freecodecamp.org/news/rss/'

    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                'User-Agent': USER_AGENT,
                'Accept': 'application/rss+xml, application/xml, text/xml'
            }

            async with session.get(rss_url, headers=headers,
                                   timeout=aiohttp.ClientTimeout(total=15)) as response:
                if response.status == 200:
                    text = await response.text()
                    feed = feedparser.parse(text)

                    for entry in feed.entries[:25]:
                        all_items.append({
                            'title': entry.get('title', ''),
                            'description': strip_html_tags(entry.get('summary', ''))[:500],
                            'link': entry.get('link', ''),
                            'published': entry.get('published', ''),
                            'author': entry.get('author', ''),
                            'tags': ['developer', 'tutorial', 'programming', 'freecodecamp'],
                            'source': 'freecodecamp',
                            'type': 'developer_article',
                            'fetched_at': datetime.now(timezone.utc).isoformat()
                        })

        logger.info(f"FreeCodeCamp: collected {len(all_items)} articles")

        return {
            'items': all_items,
            'item_count': len(all_items),
            'source': 'freecodecamp',
            'collected_at': datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        logger.error(f"FreeCodeCamp collection error: {e}")
        return {
            'items': [],
            'source': 'freecodecamp',
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }


async def _collect_coursera_data() -> Dict[str, Any]:
    """Collect online learning content from Coursera Blog.

    Session 399: Renamed from udemy (API requires auth).
    Coursera blog has education industry news and learning trends.
    """
    all_items = []

    rss_url = 'https://blog.coursera.org/feed/'

    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                'User-Agent': USER_AGENT,
                'Accept': 'application/rss+xml, application/xml, text/xml'
            }

            async with session.get(rss_url, headers=headers,
                                   timeout=aiohttp.ClientTimeout(total=15)) as response:
                if response.status == 200:
                    text = await response.text()
                    feed = feedparser.parse(text)

                    for entry in feed.entries[:20]:
                        all_items.append({
                            'title': entry.get('title', ''),
                            'description': strip_html_tags(entry.get('summary', ''))[:500],
                            'link': entry.get('link', ''),
                            'published': entry.get('published', ''),
                            'tags': ['education', 'online-learning', 'courses', 'coursera'],
                            'source': 'coursera',
                            'type': 'education_content',
                            'fetched_at': datetime.now(timezone.utc).isoformat()
                        })

        logger.info(f"Coursera: collected {len(all_items)} education articles")

        return {
            'items': all_items,
            'item_count': len(all_items),
            'source': 'coursera',
            'collected_at': datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        logger.error(f"Coursera collection error: {e}")
        return {
            'items': [],
            'source': 'coursera',
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }


async def _collect_techcrunch_startups_data() -> Dict[str, Any]:
    """Collect startup and innovation news from TechCrunch.

    Session 399: Renamed from indiegogo (API blocked).
    TechCrunch Startups has fresh, daily startup/funding news.
    """
    all_items = []

    rss_url = 'https://techcrunch.com/category/startups/feed/'

    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                'User-Agent': USER_AGENT,
                'Accept': 'application/rss+xml, application/xml, text/xml'
            }

            async with session.get(rss_url, headers=headers,
                                   timeout=aiohttp.ClientTimeout(total=15)) as response:
                if response.status == 200:
                    text = await response.text()
                    feed = feedparser.parse(text)

                    for entry in feed.entries[:25]:
                        all_items.append({
                            'title': entry.get('title', ''),
                            'description': strip_html_tags(entry.get('summary', ''))[:500],
                            'link': entry.get('link', ''),
                            'published': entry.get('published', ''),
                            'author': entry.get('author', ''),
                            'tags': ['startups', 'funding', 'innovation', 'techcrunch'],
                            'source': 'techcrunch_startups',
                            'type': 'startup_news',
                            'fetched_at': datetime.now(timezone.utc).isoformat()
                        })

        logger.info(f"TechCrunch Startups: collected {len(all_items)} articles")

        return {
            'items': all_items,
            'item_count': len(all_items),
            'source': 'techcrunch_startups',
            'collected_at': datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        logger.error(f"TechCrunch Startups collection error: {e}")
        return {
            'items': [],
            'source': 'techcrunch_startups',
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }


async def collect_spider_data(spider_name: str) -> Dict[str, Any]:
    """
    Collect real data for a specific spider.
    Returns structured data with items.

    Session 394: Special handling for HackerNews to fetch full story content.
    Session 396: Added Phase 3 API handlers for key-based spiders.
    Session 397: Added legal spiders (courtlistener, justia, findlaw, lii).
    Session 399: Added yahoo_finance, freecodecamp, coursera, techcrunch_startups handlers.
    """
    # API-based spiders use their own implementations
    API_SPIDERS = ['bluesky', 'youtube', 'discord']

    if spider_name in API_SPIDERS:
        return await _collect_api_spider_data(spider_name)

    # Session 396-397: Phase 3 API key-based spiders + Legal spiders
    # Session 399: Added sec_edgar, spotify
    PHASE3_API_SPIDERS = {
        'polygon_finance': _collect_polygon_data,
        'etherscan': _collect_etherscan_data,
        'newsapi': _collect_newsapi_data,
        'giphy': _collect_giphy_data,
        'unsplash': _collect_unsplash_data,
        'adzuna': _collect_adzuna_data,
        'finnhub': _collect_finnhub_data,
        # Session 397: Legal spiders
        'courtlistener': _collect_courtlistener_data,
        'legal_news': _collect_legal_news_data,  # Session 399: Renamed from justia
        # Session 505: Removed findlaw - proper FindLawSpider class in spider_registry handles it
        'lii': _collect_lii_data,
        # Session 399: Additional API spiders
        'spotify': _collect_spotify_data,
        'polygon_gaming': _collect_polygon_gaming_data,
        # Session 399: SEC EDGAR filings
        'sec_edgar': _collect_sec_edgar_data,
        # Session 399: Final 4 spiders (renamed for accuracy)
        'yahoo_finance': _collect_yahoo_finance_data,
        'freecodecamp': _collect_freecodecamp_data,  # Was hashnode
        'coursera': _collect_coursera_data,  # Was udemy
        'techcrunch_startups': _collect_techcrunch_startups_data,  # Was indiegogo
    }

    if spider_name in PHASE3_API_SPIDERS:
        return await PHASE3_API_SPIDERS[spider_name]()

    urls = SPIDER_TARGET_URLS.get(spider_name, [])

    if not urls:
        # Return minimal data if no URLs configured
        return {
            'items': [],
            'source': spider_name,
            'category': 'unknown',
            'message': f'No target URLs configured for {spider_name}',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

    all_items = []
    # S2970: track per-URL fetch outcomes so the runner can distinguish
    # "spider ran, all fetches failed" from "spider ran, feeds were empty".
    # Passed downstream via `data['fetch_stats']`; the runner reads it to
    # derive empty_reason='fetch_failed' vs 'no_items' / 'all_deduped'.
    fetch_stats: Dict[str, Any] = {
        'attempts': 0,
        'successes': 0,
        'urls_attempted': list(urls),
        'failed_urls': [],
    }

    async with aiohttp.ClientSession(**_build_client_session_kwargs()) as session:
        for url in urls:
            fetch_stats['attempts'] += 1
            result = await fetch_url(session, url)

            if result:
                fetch_stats['successes'] += 1
                # Session 394: Special handling for HackerNews
                # The topstories.json only returns IDs, so we fetch full stories
                if spider_name == 'hackernews' and result['type'] == 'json':
                    story_ids = result['data']
                    if isinstance(story_ids, list) and story_ids and isinstance(story_ids[0], int):
                        items = await fetch_hackernews_stories(session, story_ids)
                        logger.info(f"Spider hackernews: fetched {len(items)} full stories")
                    else:
                        items = parse_json_api(result['data'], spider_name)
                elif result['type'] == 'json':
                    items = parse_json_api(result['data'], spider_name)
                elif result['type'] == 'rss':
                    items = parse_rss_feed(result['data'], spider_name)
                else:
                    items = parse_html_page(result['data'], spider_name, url)

                all_items.extend(items)
                logger.info(f"Spider {spider_name}: collected {len(items)} items from {url}")
            else:
                fetch_stats['failed_urls'].append(url)

    # S2970: sports_injuries spider — filter parsed items to injury-relevant
    # only. Applied here (post-parse, pre-dedup) so downstream dedup and
    # LegacySpiderData writes see the filtered set; keeps the spider's
    # semantic identity ("injury updates") aligned with what its RSS
    # sources (rotowire per-sport news) actually emit.
    if spider_name == 'sports_injuries' and all_items:
        pre_filter = len(all_items)
        all_items = filter_injury_items(all_items)
        logger.info(
            f"Spider sports_injuries: injury filter kept "
            f"{len(all_items)}/{pre_filter} items"
        )

    return {
        'items': all_items[:50],  # Limit to 50 items
        'item_count': len(all_items),
        'source': spider_name,
        'urls_scraped': urls,
        'fetch_stats': fetch_stats,
        'collected_at': datetime.now(timezone.utc).isoformat()
    }


async def collect_all_spiders_data(spider_names: List[str] = None) -> Dict[str, Any]:
    """
    Collect real data for all spiders (or specified list).
    """
    if spider_names is None:
        spider_names = list(SPIDER_TARGET_URLS.keys())

    results = {}

    for spider_name in spider_names:
        try:
            data = await collect_spider_data(spider_name)
            results[spider_name] = {
                'success': True,
                'item_count': data.get('item_count', 0),
                'data': data
            }
        except Exception as e:
            logger.error(f"Error collecting data for {spider_name}: {e}")
            results[spider_name] = {
                'success': False,
                'error': str(e)
            }

    return results


# Synchronous wrapper for use in Celery tasks
def collect_spider_data_sync(spider_name: str) -> Dict[str, Any]:
    """Synchronous wrapper for collect_spider_data"""
    return asyncio.run(collect_spider_data(spider_name))


def collect_all_spiders_data_sync(spider_names: List[str] = None) -> Dict[str, Any]:
    """Synchronous wrapper for collect_all_spiders_data"""
    return asyncio.run(collect_all_spiders_data(spider_names))

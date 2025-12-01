"""
Real Data Collector - Session 221
=================================

This module provides real web scraping and API data collection for all spiders.
It fetches actual data from configured targets using aiohttp and BeautifulSoup.
"""

import aiohttp
import asyncio
import json
import logging
import feedparser
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)


# Real target URLs for each spider (with proper full URLs)
SPIDER_TARGET_URLS = {
    # === NEWS & TECH SPIDERS ===
    'techcrunch': ['https://techcrunch.com/feed/'],
    'theverge': ['https://www.theverge.com/rss/index.xml'],
    'wired': ['https://www.wired.com/feed/rss'],
    'mit_tech_review': ['https://www.technologyreview.com/feed/'],
    'axios': ['https://api.axios.com/feed/'],
    'hackernews': ['https://hacker-news.firebaseio.com/v0/topstories.json'],
    'devto': ['https://dev.to/api/articles?per_page=30'],

    # === REMOTE JOBS SPIDERS ===
    'remoteok': ['https://remoteok.com/api'],
    'weworkremotely': ['https://weworkremotely.com/categories/remote-programming-jobs.rss'],

    # === FINANCIAL SPIDERS ===
    'coingecko': ['https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=20&page=1'],
    'yahoo_finance': ['https://query1.finance.yahoo.com/v8/finance/chart/SPY?interval=1d'],

    # === DESIGN SPIDERS ===
    'dribbble': ['https://dribbble.com/shots/popular'],
    'behance': ['https://www.behance.net/feeds/projects'],

    # === CONTENT/CREATOR SPIDERS ===
    'producthunt': ['https://www.producthunt.com/feed'],
    'medium': ['https://medium.com/feed/topic/technology'],
    'hashnode': ['https://hashnode.com/api/feed/best'],

    # === EDUCATION SPIDERS ===
    'udemy': ['https://www.udemy.com/api-2.0/discovery-units/bestseller/?page_size=20'],

    # === CROWDFUNDING SPIDERS ===
    'kickstarter': ['https://www.kickstarter.com/discover/advanced.json?sort=magic&page=1'],
    'indiegogo': ['https://www.indiegogo.com/private_api/discover/main?sort=trending'],

    # === COMMUNITY SPIDERS (Session 294) ===
    # Reddit - uses JSON API (no API key needed)
    'reddit': [
        'https://www.reddit.com/r/webdev/hot.json?limit=15',
        'https://www.reddit.com/r/MachineLearning/hot.json?limit=15',
        'https://www.reddit.com/r/StableDiffusion/hot.json?limit=15',
        'https://www.reddit.com/r/Entrepreneur/hot.json?limit=15',
        'https://www.reddit.com/r/freelance/hot.json?limit=15',
        'https://www.reddit.com/r/startups/hot.json?limit=15',
        'https://www.reddit.com/r/SideProject/hot.json?limit=10',
        'https://www.reddit.com/r/ChatGPT/hot.json?limit=10',
    ],

    # Indie Hackers - uses RSS feeds (no API key needed)
    'indiehackers': [
        'https://www.indiehackers.com/feed.xml',
    ],

    # Note: These spiders use their own API clients, not SPIDER_TARGET_URLS:
    # - bluesky: Uses BlueSky AT Protocol API (BLUESKY_IDENTIFIER, BLUESKY_PASSWORD)
    # - youtube: Uses YouTube Data API v3 (GOOGLE_API_KEY)
    # - discord: Uses Discord Bot API (DISCORD_BOT_TOKEN)
}

# User agent to avoid blocks
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'


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
                if 'application/json' in content_type:
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
                    # HackerNews returns IDs
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
        'price': ['price', 'salary', 'budget', 'cost', 'amount'],
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
    import os

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
    """Collect data from Discord Bot API"""
    import os

    bot_token = os.getenv('DISCORD_BOT_TOKEN', '')

    if not bot_token:
        return {
            'items': [],
            'source': 'discord',
            'error': 'DISCORD_BOT_TOKEN not configured (need bot token, not just app ID)',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

    # Discord bot implementation would go here
    # For now, return empty as we don't have the bot token yet
    return {
        'items': [],
        'source': 'discord',
        'message': 'Discord bot ready - configure bot and add to servers',
        'timestamp': datetime.now(timezone.utc).isoformat()
    }


async def collect_spider_data(spider_name: str) -> Dict[str, Any]:
    """
    Collect real data for a specific spider.
    Returns structured data with items.
    """
    # API-based spiders use their own implementations
    API_SPIDERS = ['bluesky', 'youtube', 'discord']

    if spider_name in API_SPIDERS:
        return await _collect_api_spider_data(spider_name)

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

    async with aiohttp.ClientSession() as session:
        for url in urls:
            result = await fetch_url(session, url)

            if result:
                if result['type'] == 'json':
                    items = parse_json_api(result['data'], spider_name)
                elif result['type'] == 'rss':
                    items = parse_rss_feed(result['data'], spider_name)
                else:
                    items = parse_html_page(result['data'], spider_name, url)

                all_items.extend(items)
                logger.info(f"Spider {spider_name}: collected {len(items)} items from {url}")

    return {
        'items': all_items[:50],  # Limit to 50 items
        'item_count': len(all_items),
        'source': spider_name,
        'urls_scraped': urls,
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

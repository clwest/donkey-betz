"""
NOAA Spider - Weather & Climate Intelligence
=============================================

Session 534: Simplified to work with spider network interface.
Uses NOAA API when available, RSS fallback for weather news.
"""

from ai_core.spiders.web_request_layer import cached_get
import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class NOAASpider:
    """NOAA spider - weather alerts, forecasts, and climate data"""

    name = "noaa"

    BASE_URL = "https://api.weather.gov"

    # Weather news RSS feeds (fallback)
    RSS_FEEDS = {
        'weather_underground': 'https://www.wunderground.com/rss/wxfeeds.xml',
        'accuweather_news': 'https://www.accuweather.com/en/weather-news.rss',
        'noaa_news': 'https://www.noaa.gov/news/rss.xml',
        'climate_central': 'https://www.climatecentral.org/feed',
    }

    # Weather categories
    CATEGORIES = [
        ('Alerts', 'alerts', 'Active weather alerts.'),
        ('Forecasts', 'forecast', 'Weather forecasts.'),
        ('Climate', 'climate', 'Climate news and data.'),
        ('Severe', 'severe', 'Severe weather events.'),
        ('Tropical', 'tropical', 'Tropical weather updates.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.weather_categories = {
            'severe': ['severe', 'warning', 'watch', 'tornado', 'hurricane', 'flood'],
            'winter': ['winter', 'snow', 'ice', 'blizzard', 'cold', 'freeze'],
            'heat': ['heat', 'hot', 'temperature', 'record', 'heatwave'],
            'storm': ['storm', 'thunder', 'lightning', 'wind', 'rain'],
            'tropical': ['tropical', 'hurricane', 'cyclone', 'typhoon'],
            'climate': ['climate', 'drought', 'trend', 'pattern', 'change'],
        }

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch weather data from NOAA API and RSS feeds.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of weather content dictionaries
        """
        all_items = []
        seen_urls = set()

        # Try NOAA API for alerts
        try:
            api_items = self._fetch_noaa_alerts()
            for item in api_items:
                if item.get('url', item.get('id', '')) not in seen_urls:
                    seen_urls.add(item.get('url', item.get('id', '')))
                    all_items.append(item)
        except Exception as e:
            logger.warning(f"Error fetching NOAA alerts: {e}")

        # Fetch from RSS feeds
        for feed_name, feed_url in self.RSS_FEEDS.items():
            try:
                items = self._fetch_rss(feed_url, feed_name)
                for item in items:
                    if item['url'] not in seen_urls:
                        seen_urls.add(item['url'])
                        all_items.append(item)
            except Exception as e:
                logger.warning(f"Error fetching {feed_name} feed: {e}")

        # Add category links
        try:
            categories = self._get_category_links()
            all_items.extend(categories)
        except Exception as e:
            logger.warning(f"Error getting weather categories: {e}")

        # If all sources fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"NOAA spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_noaa_alerts(self) -> List[Dict[str, Any]]:
        """Fetch active weather alerts from NOAA API."""
        items = []

        try:
            headers = {
                'User-Agent': 'WeatherSpider/1.0',
                'Accept': 'application/geo+json'
            }

            response = cached_get(
                f"{self.BASE_URL}/alerts/active",
                headers=headers,
                params={'status': 'actual', 'limit': 30},
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                features = data.get('features', [])

                for feature in features[:20]:
                    props = feature.get('properties', {})
                    severity = props.get('severity', '')
                    event = props.get('event', '')

                    items.append({
                        'title': props.get('headline', event),
                        'url': props.get('id', ''),
                        'link': f"https://alerts.weather.gov",
                        'summary': props.get('description', '')[:400] if props.get('description') else '',
                        'description': props.get('description', '')[:400] if props.get('description') else '',
                        'event_type': event,
                        'severity': severity,
                        'urgency': props.get('urgency', ''),
                        'area': props.get('areaDesc', ''),
                        'effective': props.get('effective', ''),
                        'expires': props.get('expires', ''),
                        'category': self._detect_category(f"{event} {props.get('description', '')}".lower()),
                        'is_severe': severity in ['Extreme', 'Severe'],
                        'source': 'NOAA',
                        'data_type': 'weather_alert',
                        'platform': 'noaa',
                        'tags': ['noaa', 'weather', 'alert', severity.lower()],
                        'timestamp': datetime.now().isoformat(),
                    })

        except Exception as e:
            logger.warning(f"Error fetching NOAA API: {e}")

        return items

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch weather news from RSS feed."""
        items = []

        try:
            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:12]:
                title = entry.get('title', '')
                if not title:
                    continue

                url = entry.get('link', '')
                summary = entry.get('summary', entry.get('description', ''))
                if summary:
                    summary = re.sub(r'<[^>]+>', '', summary)[:400]

                # Detect weather category
                text = f"{title} {summary}".lower()
                category = self._detect_category(text)

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': summary,
                    'description': summary,
                    'published': entry.get('published', ''),
                    'category': category,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'weather_news',
                    'platform': 'noaa',
                    'tags': ['noaa', 'weather', category],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_category(self, text: str) -> str:
        """Detect weather category from text."""
        for category, keywords in self.weather_categories.items():
            if any(kw in text for kw in keywords):
                return category
        return 'general'

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return weather category links."""
        return [
            {
                'title': f"Weather: {name}",
                'url': f'https://www.weather.gov/{slug}',
                'link': f'https://www.weather.gov/{slug}',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'NOAA',
                'data_type': 'weather_category',
                'platform': 'noaa',
                'tags': ['noaa', 'weather', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when all sources fail."""
        topics = [
            ('Weather Alerts', 'alerts', 'Active weather alerts and warnings.'),
            ('Forecasts', 'forecast', 'Weather forecasts nationwide.'),
            ('Climate Data', 'climate', 'Climate trends and patterns.'),
            ('Severe Weather', 'severe', 'Severe weather events.'),
            ('Tropical Updates', 'tropical', 'Tropical storm tracking.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://www.weather.gov/{category}',
                'link': f'https://www.weather.gov/{category}',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'NOAA',
                'data_type': 'weather_topic',
                'platform': 'noaa',
                'tags': ['noaa', 'weather', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]

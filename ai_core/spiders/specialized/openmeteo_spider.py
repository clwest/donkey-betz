"""
Open-Meteo Spider - Weather Data Intelligence
=============================================

Session 534: Simplified to work with spider network interface.
Uses Open-Meteo API (free, no key required) and RSS fallbacks.
"""

from ai_core.spiders.web_request_layer import cached_get
import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class OpenMeteoSpider:
    """Open-Meteo weather spider - free weather data for any location"""

    name = "openmeteo"

    BASE_URL = 'https://api.open-meteo.com/v1'

    # Weather RSS feeds (fallback)
    RSS_FEEDS = {
        'weather_com': 'https://weather.com/feeds/rss/news',
        'accuweather': 'https://www.accuweather.com/en/weather-news.rss',
        'weather_underground': 'https://www.wunderground.com/rss/wxfeeds.xml',
    }

    # Major US cities with coordinates
    DEFAULT_LOCATIONS = {
        'new_york': {'lat': 40.7128, 'lon': -74.0060, 'name': 'New York'},
        'los_angeles': {'lat': 34.0522, 'lon': -118.2437, 'name': 'Los Angeles'},
        'chicago': {'lat': 41.8781, 'lon': -87.6298, 'name': 'Chicago'},
        'denver': {'lat': 39.7392, 'lon': -104.9903, 'name': 'Denver'},
        'miami': {'lat': 25.7617, 'lon': -80.1918, 'name': 'Miami'},
    }

    # Weather code descriptions
    WEATHER_CONDITIONS = {
        0: 'Clear sky', 1: 'Mainly clear', 2: 'Partly cloudy', 3: 'Overcast',
        45: 'Fog', 48: 'Depositing rime fog',
        51: 'Light drizzle', 53: 'Moderate drizzle', 55: 'Dense drizzle',
        61: 'Slight rain', 63: 'Moderate rain', 65: 'Heavy rain',
        71: 'Slight snow', 73: 'Moderate snow', 75: 'Heavy snow',
        80: 'Slight rain showers', 81: 'Moderate rain showers', 82: 'Violent rain showers',
        95: 'Thunderstorm', 96: 'Thunderstorm with hail', 99: 'Thunderstorm with heavy hail',
    }

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch weather data from Open-Meteo API and RSS feeds.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of weather content dictionaries
        """
        all_items = []
        seen_keys = set()

        # Try Open-Meteo API for forecasts
        try:
            api_items = self._fetch_openmeteo_forecasts()
            for item in api_items:
                key = item.get('city', '')
                if key not in seen_keys:
                    seen_keys.add(key)
                    all_items.append(item)
        except Exception as e:
            logger.warning(f"Error fetching Open-Meteo API: {e}")

        # Fetch from RSS feeds
        for feed_name, feed_url in self.RSS_FEEDS.items():
            try:
                items = self._fetch_rss(feed_url, feed_name)
                for item in items:
                    if item['url'] not in seen_keys:
                        seen_keys.add(item['url'])
                        all_items.append(item)
            except Exception as e:
                logger.warning(f"Error fetching {feed_name} feed: {e}")

        # If all sources fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"OpenMeteo spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_openmeteo_forecasts(self) -> List[Dict[str, Any]]:
        """Fetch weather forecasts from Open-Meteo API."""
        items = []

        for city_key, location in self.DEFAULT_LOCATIONS.items():
            try:
                response = cached_get(
                    f"{self.BASE_URL}/forecast",
                    params={
                        'latitude': location['lat'],
                        'longitude': location['lon'],
                        'current': 'temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m',
                        'daily': 'temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code',
                        'temperature_unit': 'fahrenheit',
                        'wind_speed_unit': 'mph',
                        'precipitation_unit': 'inch',
                        'timezone': 'auto',
                        'forecast_days': 3,
                    },
                    timeout=10
                )

                if response.status_code == 200:
                    data = response.json()
                    current = data.get('current', {})
                    daily = data.get('daily', {})

                    weather_code = current.get('weather_code', 0)
                    condition = self.WEATHER_CONDITIONS.get(weather_code, 'Unknown')

                    items.append({
                        'title': f"{location['name']}: {condition}",
                        'url': f"openmeteo_{city_key}",
                        'link': f'https://open-meteo.com/',
                        'summary': f"Current: {current.get('temperature_2m', 'N/A')}°F, {condition}. Wind: {current.get('wind_speed_10m', 'N/A')} mph.",
                        'description': f"Temperature: {current.get('temperature_2m', 'N/A')}°F (feels like {current.get('apparent_temperature', 'N/A')}°F). Humidity: {current.get('relative_humidity_2m', 'N/A')}%.",
                        'city': location['name'],
                        'city_key': city_key,
                        'temperature': current.get('temperature_2m'),
                        'feels_like': current.get('apparent_temperature'),
                        'humidity': current.get('relative_humidity_2m'),
                        'wind_speed': current.get('wind_speed_10m'),
                        'weather_code': weather_code,
                        'condition': condition,
                        'category': 'forecast',
                        'source': 'Open-Meteo',
                        'data_type': 'weather_forecast',
                        'platform': 'openmeteo',
                        'tags': ['openmeteo', 'weather', 'forecast', city_key],
                        'timestamp': datetime.now().isoformat(),
                    })

            except Exception as e:
                logger.warning(f"Error fetching weather for {location['name']}: {e}")

        return items

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch weather news from RSS feed."""
        items = []

        try:
            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:10]:
                title = entry.get('title', '')
                if not title:
                    continue

                url = entry.get('link', '')
                summary = entry.get('summary', entry.get('description', ''))
                if summary:
                    summary = re.sub(r'<[^>]+>', '', summary)[:400]

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': summary,
                    'description': summary,
                    'published': entry.get('published', ''),
                    'category': 'news',
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'weather_news',
                    'platform': 'openmeteo',
                    'tags': ['openmeteo', 'weather', 'news'],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when all sources fail."""
        topics = [
            ('Current Weather', 'current', 'Current conditions nationwide.'),
            ('7-Day Forecast', 'forecast', 'Extended weather forecast.'),
            ('Weather Alerts', 'alerts', 'Active weather alerts.'),
            ('Climate Data', 'climate', 'Climate trends and data.'),
            ('Radar Maps', 'radar', 'Weather radar imagery.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://open-meteo.com/{category}',
                'link': f'https://open-meteo.com/{category}',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'Open-Meteo',
                'data_type': 'weather_topic',
                'platform': 'openmeteo',
                'tags': ['openmeteo', 'weather', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
